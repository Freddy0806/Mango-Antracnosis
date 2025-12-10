import flet as ft
from views.login_view import LoginView
from views.register_view import RegisterView
from views.dashboard_view import DashboardView
from views.detection_view import DetectionView
from views.report_view import ReportView
from views.profile_view import ProfileView

def main(page: ft.Page):
    page.title = "Detector de Antracnosis en Mango"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    # page.window_width = 390  # Comentado para permitir responsividad total en móvil/desktop
    # page.window_height = 844
    
    # Definir rutas
    def route_change(route):
        page.views.clear()
        
        # Default view (Login)
        if page.route == "/":
            page.views.append(LoginView(page).view())
        elif page.route == "/register":
            page.views.append(RegisterView(page).view())
        elif page.route == "/dashboard":
            page.views.append(DashboardView(page).view())
        elif page.route == "/detection":
            page.views.append(DetectionView(page).view())
        elif page.route == "/report":
            page.views.append(ReportView(page).view())
        elif page.route == "/profile":
            page.views.append(ProfileView(page).view())
            
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Start at login
    page.go("/")

if __name__ == "__main__":
    import os
    for folder in ["assets", "uploads"]:
        if not os.path.exists(folder):
            os.makedirs(folder)
        
    ft.app(target=main, assets_dir="assets", upload_dir="uploads")
