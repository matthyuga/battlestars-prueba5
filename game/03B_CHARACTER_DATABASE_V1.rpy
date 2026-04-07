# ============================================================
# 03B_CHARACTER_DATABASE_V1.RPY – Base de datos de personajes
# ============================================================
# Versión: v1 (Tier C inicial)
# ------------------------------------------------------------
# - Base en Ren'Py (sin SQL)
# - Dataset inicial de personajes Tier C
# - Helpers para obtener por tier / franquicia / nombre
# ============================================================

init -960 python:

    import renpy.store as S

    # ------------------------------------------------------------
    # Dataset canónico inicial (Tier C)
    # ------------------------------------------------------------
    CHARACTER_DB = [
        {"name": "Aqua", "franchise": "KonoSuba", "tier": "C"},
        {"name": "Kazuma", "franchise": "KonoSuba", "tier": "C"},
        {"name": "Darkness", "franchise": "KonoSuba", "tier": "C"},
        {"name": "Megumin", "franchise": "KonoSuba", "tier": "C"},
        {"name": "Sakura", "franchise": "Naruto", "tier": "C"},
        {"name": "Ino", "franchise": "Naruto", "tier": "C"},
        {"name": "Hanabi", "franchise": "Naruto", "tier": "C"},
        {"name": "Boruto", "franchise": "Naruto", "tier": "C"},
        {"name": "Kiba", "franchise": "Naruto", "tier": "C"},
        {"name": "Shino", "franchise": "Naruto", "tier": "C"},
        {"name": "Choji", "franchise": "Naruto", "tier": "C"},
        {"name": "Shikamaru", "franchise": "Naruto", "tier": "C"},
        {"name": "Karin", "franchise": "Naruto", "tier": "C"},
        {"name": "Danny Phantom", "franchise": "Danny Phantom", "tier": "C"},
        {"name": "Yanfei", "franchise": "Genshin Impact", "tier": "C"},
        {"name": "Amber", "franchise": "Genshin Impact", "tier": "C"},
        {"name": "Ryuko", "franchise": "Kill la Kill", "tier": "C"},
        {"name": "Nobara", "franchise": "Jujutsu Kaisen", "tier": "C"},
        {"name": "Maki (Atadura Celestial)", "franchise": "Jujutsu Kaisen", "tier": "C"},
        {"name": "Yor Forger", "franchise": "Spy x Family", "tier": "C"},
        {"name": "Revy", "franchise": "Black Lagoon", "tier": "C"},
        {"name": "Shadowheart", "franchise": "Baldur's Gate 3", "tier": "C"},
        {"name": "Lae'zel", "franchise": "Baldur's Gate 3", "tier": "C"},
        {"name": "Elizabeth", "franchise": "BioShock", "tier": "C"},
        {"name": "Shrinking Rae", "franchise": "Invincible", "tier": "C"},
        {"name": "Bloom", "franchise": "Winx Club", "tier": "C"},
        {"name": "Bertrand", "franchise": "KamiKatsu: Working for God in a Godless World", "tier": "C"},
        {"name": "The Twins", "franchise": "Atomic Heart", "tier": "C"},
    ]

    # ------------------------------------------------------------
    # Índices auxiliares
    # ------------------------------------------------------------
    def _normalize_text(v):
        try:
            text_type = unicode
        except:
            text_type = str
        try:
            return text_type(v).strip().lower()
        except:
            try:
                return str(v).strip().lower()
            except:
                return ""

    def get_characters_by_tier(tier):
        t = _normalize_text(tier).upper()
        return [c for c in CHARACTER_DB if c.get("tier", "") == t]

    def get_characters_by_franchise(franchise):
        f = _normalize_text(franchise)
        return [c for c in CHARACTER_DB if _normalize_text(c.get("franchise", "")) == f]

    def get_character_by_name(name):
        n = _normalize_text(name)
        for c in CHARACTER_DB:
            if _normalize_text(c.get("name", "")) == n:
                return c
        return None

    def get_character_count_by_tier(tier):
        return len(get_characters_by_tier(tier))

    # Export a store para uso en pantallas/labels
    S.CHARACTER_DB = CHARACTER_DB
    S.get_characters_by_tier = get_characters_by_tier
    S.get_characters_by_franchise = get_characters_by_franchise
    S.get_character_by_name = get_character_by_name
    S.get_character_count_by_tier = get_character_count_by_tier
