# django_core_micha/scripts/generate_env.py
import argparse
import os
import sys
import yaml # pip install PyYAML
import re

def get_secret(key, default=None, required=False):
    """Retrieves a secret from env vars (CI) or returns default."""
    val = os.environ.get(key, default)
    if required and not val:
        print(f"❌ Error: Secret '{key}' is required but not set in environment.")
        sys.exit(1)
    return val

def write_env_file(path, lines):
    """Helper to write the list of lines to the .env file."""
    try:
        with open(path, "w") as f:
            f.write("\n".join(lines))
            f.write("\n")
        print(f"✅ Successfully wrote {path}")
    except Exception as e:
        print(f"❌ Error writing file: {e}")
        sys.exit(1)
def parse_env_file(path):
    """Parses a simple .env file and returns a dictionary."""
    if not os.path.exists(path):
        return {}
    
    data = {}
    
    # Regex, um KEY=VALUE oder KEY="VALUE" zu matchen und Kommentare (#) zu ignorieren
    env_regex = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$')

    with open(path, 'r') as f:
        for line in f:
            match = env_regex.search(line)
            if match:
                key = match.group(1)
                value = match.group(2).strip()
                
                # Entferne umgebende Anführungszeichen falls vorhanden
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                
                data[key] = value
                
    return data

def generate_env(env_name, config_path="project.yaml", output_path=".env"):
    print(f"⚙️  Generating .env for environment: {env_name}")
    
    if not os.path.exists(config_path):
        print(f"❌ Error: Config file '{config_path}' not found.")
        sys.exit(1)

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    project_type = config.get("project_type", "django")

    # 1. Validate Environment exists in YAML
    if env_name not in config.get("environments", {}):
        if env_name == "local" and project_type == "infrastructure":
            print("ℹ️  Infrastructure app does not require local .env generation. Exiting.")
            sys.exit(0)
            
        print(f"❌ Error: Environment '{env_name}' not found in {config_path}")
        sys.exit(1)

    env_config = config["environments"][env_name]
    env_overrides = env_config.get("env_overrides", {})
    env_content = []

    # ==========================================
    # MODE A: INFRASTRUCTURE
    # ==========================================
    if project_type == "infrastructure":
        print("🏗️  Generating Infrastructure .env")
        # [Infrastructure logic omitted for brevity - logic remains identical]
        domain_map = env_config.get("domains", {})
        for var_name, domain in domain_map.items():
            env_content.append(f"{var_name}={domain}")

        infra_secrets = ["TRAEFIK_DASHBOARD_AUTH", "ACME_EMAIL", "WG_SERVERURL", "WG_PEERS"]
        for secret in infra_secrets:
            if secret in env_overrides:
                val = env_overrides[secret]
            else:
                val = get_secret(secret, required=False)
            
            if val:
                if secret == "TRAEFIK_DASHBOARD_AUTH": val = val.replace("$", "$$")
                env_content.append(f"{secret}={val}")

        env_content.append(f"CONTAINER_NAME_PREFIX={config.get('container_prefix', 'infra')}")
        write_env_file(output_path, env_content)
        return

    # ==========================================
    # MODE B: STANDARD DJANGO APP
    # ==========================================
    domains = env_config.get("domains", [])
    use_traefik = env_config.get("use_traefik", False)
    is_local = (env_name == "local")
    local_defaults = env_config.get("defaults", {})

    local_secrets = {}
    if is_local:
        local_secrets = parse_env_file(".env.local")
        if local_secrets:
             print("ℹ️  Found and integrated secrets from .env.local")

    base_prefix = config.get("container_prefix", "app")

    if env_name == "staging":
        ctr_prefix = f"{base_prefix}_stage"
    elif env_name == "production":
        ctr_prefix = f"{base_prefix}_prod"
    else:
        ctr_prefix = base_prefix

    def resolve(key, required_in_prod=True, default=""):
        """
        Holt einen Wert für 'key' aus
        1) env_overrides (project.yaml)
        2) lokalen Secrets (.env.local, NUR wenn is_local=True)
        3) lokalen defaults (local/.env-Defaults)
        4) optional OS-Umgebung
        5) oder (falls nötig) get_secret()
        """
        # 1) Override aus project.yaml
        if key in env_overrides:
            return env_overrides[key]
        
        # 2) NEU: Lokale Secrets aus .env.local (nur im lokalen Modus)
        if is_local and key in local_secrets:
            return local_secrets[key]
            
        # 3) Lokale Defaults (für ENV=local)
        if is_local and key in local_defaults:
            return local_defaults.get(key, default)

        # 4) Direktes OS-Environment (z.B. aus CI)
        env_val = os.environ.get(key)
        if env_val:
            return env_val

        # 5) Fallback auf default, falls angegeben
        if default != "":
            return default

        # 6) Secret aus Umgebung holen (kann required sein)
        return get_secret(key, required=required_in_prod)

    # --- Database ---
    prod_env = config.get("environments", {}).get("production", {})
    prod_domains = prod_env.get("domains", [])
    primary_domain = prod_domains[0] if prod_domains else None

    default_master_base = None
    if primary_domain:
        default_master_base = f"https://{primary_domain}"

    # ...

    env_content.append(f"ENV_TYPE={env_name}")
    debug_val = resolve("DEBUG", required_in_prod=False)
    env_content.append(f"DEBUG={debug_val or 'False'}")

    # MASTER_BASE_URL: wenn Secret gesetzt → das nehmen, sonst Default aus project.yaml
    if default_master_base:
        env_content.append(
            f"MASTER_BASE_URL={resolve('MASTER_BASE_URL', required_in_prod=False, default=default_master_base)}"
        )
    
    env_content.append(f"# --- Database ---")
    env_content.append(f"DB_USER={resolve('DB_USER')}")
    env_content.append(f"DB_PASSWORD={resolve('DB_PASSWORD')}")
    env_content.append(f"DB_NAME={resolve('DB_NAME')}")

    # DB_HOST: Priorität
    # 1) env_overrides["DB_HOST"] (project.yaml)
    # 2) Secret DB_HOST aus Umgebung (z. B. GitHub)
    # 3) fallback:
    #    - local: "db"
    #    - staging: "<ctr_prefix>_db" (z. B. innoservice_stage_db)
    #    - production: "<ctr_prefix>_db" (z. B. innoservice_prod_db)
    #    - sonst: "<ctr_prefix>_db"
    if "DB_HOST" in env_overrides:
        db_host = env_overrides["DB_HOST"]
    else:
        secret_db_host = os.environ.get("DB_HOST", "")
        if secret_db_host:
            db_host = secret_db_host
        else:
            if is_local:
                db_host = "db"
            else:
                db_host = f"{ctr_prefix}_db"

    env_content.append(f"DB_HOST={db_host}")
    env_content.append(f"DB_PORT={resolve('DB_PORT')}")

    # --- Django ---
    env_content.append(f"\n# --- KEYS ---")
    env_content.append(f"DJANGO_SECRET_KEY={resolve('DJANGO_SECRET_KEY', required_in_prod=True)}")
    env_content.append(f"VITE_APP_MUI_LICENSE_KEY={resolve('VITE_APP_MUI_LICENSE_KEY', required_in_prod=False)}")
    env_content.append(f"SYNC_SHARED_SECRET={resolve('SYNC_SHARED_SECRET', required_in_prod=False)}")
    env_content.append(f"DEEPL_API_KEY={resolve('DEEPL_API_KEY', required_in_prod=False)}")
    env_content.append(f"ORIGIN_SERVER_ID={resolve('ORIGIN_SERVER_ID', required_in_prod=False)}")

    if not is_local and str(debug_val).lower() == "true":
        print("❌ Error: DEBUG=True is not allowed in non-local environments.")
        sys.exit(1)

    # --- Mail ---
    env_content.append(f"\n# --- Mail ---")
    if is_local:
        env_content.append("EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend")
    else:
        env_content.append(f"EMAIL_HOST={resolve('EMAIL_HOST', required_in_prod=False)}")
        env_content.append(f"EMAIL_PORT={resolve('EMAIL_PORT', required_in_prod=False)}")
        env_content.append(f"EMAIL_USE_TLS={resolve('EMAIL_USE_TLS', required_in_prod=False)}")
        env_content.append(f"EMAIL_USER={resolve('EMAIL_USER', required_in_prod=False)}")
        env_content.append(f"EMAIL_PASSWORD={resolve('EMAIL_PASSWORD', required_in_prod=False)}")
        env_content.append(f"DEFAULT_FROM_EMAIL={resolve('EMAIL_USER', required_in_prod=False)}")

        
    
    ex_key = resolve("EXCHANGERATE_HOST_KEY", required_in_prod=False)
    if ex_key:
        env_content.append(f"EXCHANGERATE_HOST_KEY={ex_key}")

    # --- Infrastructure ---
    env_content.append(f"\n# --- Infrastructure ---")
    
    # Fetch the base prefix (now "jg_ferien")
    
    
    env_content.append(f"CONTAINER_NAME_PREFIX={ctr_prefix}")
    env_content.append(f"ROUTER_NAME={config.get('project_name')}-{env_name}")

    project_name = config.get("project_name", "Project")
    env_content.append(f"MFA_WEBAUTHN_RP_NAME={project_name}")
    env_content.append(f"PROJECT_NAME={project_name}")

    # --- VOLUMES (New Section) ---
    vol_config = env_config.get("volumes", {})
    
    def get_vol_name(key, default_name):
        val = vol_config.get(key)
        # Handle dict format (e.g., {external: true, name: 'foo'})
        if isinstance(val, dict):
            return val.get("name", default_name)
        # Handle simple string format or None
        return val if val else default_name

    db_vol = get_vol_name("postgres_data", f"{ctr_prefix}_postgres_data")
    media_vol = get_vol_name("media_volume", f"{ctr_prefix}_media_volume")
    excel_vol = get_vol_name("excel_volume", f"{ctr_prefix}_excel_volume")

    env_content.append(f"DB_VOLUME_NAME={db_vol}")
    env_content.append(f"MEDIA_VOLUME_NAME={media_vol}")
    env_content.append(f"EXCEL_VOLUME_NAME={excel_vol}")

    # --- Network ---
    defaults = env_config.get('defaults', {})
    
    # Wir suchen nach WEB_PORT (wie in yaml) oder webport (fallback), standard 8000
    web_port = defaults.get('WEB_PORT') or env_config.get('webport') or 8000

    main_domain = domains[0] if domains else "localhost"
    env_content.append(f"DJANGO_ALLOWED_HOSTS={','.join(domains)}")
    protocol = "https" if use_traefik else "http"
    csrf_urls = [f"{protocol}://{d}" for d in domains]
    if is_local:
        # 1. Standard React Port (immer gut zu haben)
        csrf_urls.extend(["http://localhost:3000", "http://127.0.0.1:3000"])
        
        # 2. NEU: Dynamischer Port aus der project.yaml (z.B. 8126)
        # Lese den Port aus der Konfiguration (pass den Key an deine YAML-Struktur an)
        # Meistens hast du ihn schon in einer Variable wie 'web_port' für die .env gespeichert
        
        # Angenommen, du hast eine Variable 'web_port' oder liest es so:
        local_port = web_port # Fallback 8000, falls nichts definiert
        
        # Füge localhost + IP mit diesem Port hinzu
        csrf_urls.append(f"http://localhost:{local_port}")
        csrf_urls.append(f"http://127.0.0.1:{local_port}")
        
    env_content.append(f"CSRF_TRUSTED_URLS={','.join(csrf_urls)}")
    if is_local or not use_traefik:
        origin = f"{protocol}://{main_domain}:{web_port}"
    else:
        origin = f"{protocol}://{main_domain}"

    env_content.append(f"PUBLIC_ORIGIN={origin}")

    if use_traefik:
        rules = [f"Host(`{d}`)" for d in domains]
        env_content.append(f"TRAEFIK_ROUTER_RULE={' || '.join(rules)}")
    else:
        env_content.append("TRAEFIK_ROUTER_RULE=Host(`localhost`)")

   
    # --- Auth / Social Secrets ---
    env_content.append(f"\n# --- Social Auth ---")
    # Google
    env_content.append(f"GOOGLE_CLIENT_ID={resolve('GOOGLE_CLIENT_ID', required_in_prod=False)}")
    env_content.append(f"GOOGLE_SECRET={resolve('GOOGLE_SECRET', required_in_prod=False)}")
    # Microsoft
    env_content.append(f"MICROSOFT_CLIENT_ID={resolve('MICROSOFT_CLIENT_ID', required_in_prod=False)}")
    env_content.append(f"MICROSOFT_SECRET={resolve('MICROSOFT_SECRET', required_in_prod=False)}")
    env_content.append(f"MICROSOFT_TENANT_ID={resolve('MICROSOFT_TENANT_ID', required_in_prod=False)}")

    env_content.append(f"WEB_PORT={resolve('WEB_PORT', required_in_prod=False) or '8125'}")
    env_content.append(f"DB_HOST_PORT={resolve('DB_HOST_PORT', required_in_prod=False) or '5435'}")

    write_env_file(output_path, env_content)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True, help="Environment (production, staging, local)")
    # Default output ist nun das aktuelle Verzeichnis, wo der Befehl ausgeführt wird
    parser.add_argument("--output", default=".env", help="Output file path")
    # Optional: Config-Pfad konfigurierbar machen, default auf aktuelles Dir
    parser.add_argument("--config", default="project.yaml", help="Path to project.yaml")
    
    args = parser.parse_args()
    
    # Übergib args.config an generate_env
    generate_env(args.env, config_path=args.config, output_path=args.output)

if __name__ == "__main__":
    main()