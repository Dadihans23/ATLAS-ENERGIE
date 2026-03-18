"""
Middleware de sécurité – headers HTTP défensifs.

Couvre :
- Content-Security-Policy (HIGH-02)
- Permissions-Policy (MEDIUM-02)
- Referrer-Policy
"""


class SecurityHeadersMiddleware:
    """
    Ajoute des headers de sécurité sur chaque réponse HTTP.
    À placer tôt dans MIDDLEWARE (après SecurityMiddleware).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # ── Content-Security-Policy ──────────────────────────────────────────
        # Autorise les CDNs utilisés (Tailwind, DaisyUI, Google Fonts)
        # 'unsafe-inline' nécessaire pour les styles/scripts inline des templates
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: blob:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )

        # ── Permissions-Policy (MEDIUM-02) ───────────────────────────────────
        # Désactive les APIs sensibles du navigateur inutilisées par l'app
        response['Permissions-Policy'] = (
            "camera=(), microphone=(), geolocation=(), payment=(), "
            "usb=(), magnetometer=(), gyroscope=(), accelerometer=()"
        )

        # ── Referrer-Policy ──────────────────────────────────────────────────
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        return response
