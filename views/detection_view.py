import flet as ft
from controllers.detection_controller import detection_controller

class DetectionView:
    def __init__(self, page: ft.Page):
        self.page = page

    def view(self):
        img_control = ft.Image(src="", width=300, height=300, fit=ft.ImageFit.CONTAIN, visible=False)
        result_text = ft.Text(size=16)
        treatment_text = ft.Text(size=14, color="blue_grey")
        

        # Variables de estado para alternar imágenes
        current_image_state = {"original": "", "processed": "", "showing_original": True}
        
        toggle_btn = ft.ElevatedButton("Ver Imagen Procesada (IA)", icon="visibility", visible=False)

        def toggle_image(_):
            if current_image_state["showing_original"]:
                img_control.src = current_image_state["processed"]
                toggle_btn.text = "Ver Original"
                toggle_btn.icon = "visibility_off"
                current_image_state["showing_original"] = False
            else:
                img_control.src = current_image_state["original"]
                toggle_btn.text = "Ver Imagen Procesada (IA)"
                toggle_btn.icon = "visibility"
                current_image_state["showing_original"] = True
            img_control.update()
            toggle_btn.update()

        toggle_btn.on_click = toggle_image

        def run_analysis(file_path, file_name):
            # Resetear estado
            current_image_state["original"] = file_path # Ruta para el backend (assets/img.jpg)
            # Para la web, como assets_dir="assets", la url es /img.jpg
            web_path = f"/{file_name}" 
            
            current_image_state["showing_original"] = True
            
            # Usamos un truco con time para romper cache del navegador si se sube el mismo nombre
            import time
            img_control.src = f"{web_path}?{time.time()}"
            img_control.visible = True
            
            toggle_btn.visible = False
            toggle_btn.text = "Ver Imagen Procesada (IA)"
            toggle_btn.icon = "visibility"
            
            result_text.value = "Procesando imagen..."
            result_text.color = "blue"
            
            img_control.update()
            toggle_btn.update()
            result_text.update()
            
            # Run detection
            # NOTA: DetectionController lee del sistema de archivos, así que necesita la ruta local (assets/...)
            result = detection_controller.detect_disease(file_path)
            
            if "error" in result:
                result_text.value = f"Error: {result['error']}"
                result_text.color = "red"
            else:
                status = result["status"]
                phase = result["phase"]
                confidence = result["confidence"]
                treatment = result["treatment"]
                
                # Configurar imagen procesada
                if "processed_image" in result:
                    # processed_image viene como 'assets/processed_...'
                    # para web necesitamos '/processed_...'
                    proc_path = result["processed_image"].replace("\\", "/")
                    if proc_path.startswith("assets/"):
                        proc_path = "/" + proc_path[7:]
                    current_image_state["processed"] = proc_path
                    
                    toggle_btn.visible = True
                    toggle_btn.update()
                
                color = "green" if status == "Sano" else "red"
                result_text.value = f"Resultado: {status}\nFase: {phase}\nDaño: {result['infection_ratio']:.2f}%"
                result_text.color = color
                
                treatment_text.value = f"Tratamiento Recomendado:\n{treatment}"
            
            result_text.update()
            treatment_text.update()

        def on_upload_complete(e: ft.FilePickerUploadEvent):
            if e.error:
                result_text.value = f"Error de Subida: {e.error}"
                result_text.color = "red"
                result_text.update()
                return

            if e.progress and e.progress < 1.0:
                 return

            if e.file_name:
                import os
                import shutil
                
                cwd = os.getcwd()
                # Ruta estándar de uploads
                upload_path = os.path.join(cwd, "uploads", e.file_name)
                # Ruta final en assets
                final_path = os.path.join(cwd, "assets", e.file_name)
                
                result_text.value = f"Procesando id:{e.file_name}..."
                result_text.update()
                
                # Esperar un momento breve por si el filesystem está lento
                import time
                time.sleep(0.5)

                if os.path.exists(upload_path):
                    try:
                        if os.path.exists(final_path):
                            os.remove(final_path)
                        shutil.move(upload_path, final_path)
                        run_analysis(final_path, e.file_name)
                    except Exception as ex:
                         result_text.value = f"Error moviendo: {ex}"
                         result_text.color = "red"
                         result_text.update()
                else:
                    # Fallback: A veces Flet guarda con nombre temporal o en assets directo si falla la config
                    # Buscamos en assets por si acaso
                    if os.path.exists(final_path):
                         run_analysis(final_path, e.file_name)
                    else:
                        result_text.value = f"Error: Archivo no aparece.\n{upload_path}"
                        result_text.color = "red"
                        result_text.update()

        def on_dialog_result(e: ft.FilePickerResultEvent):
            if e.files:
                # Si estamos en WEB, necesitamos subir el archivo al servidor
                if self.page.web:
                    # "Hack" para subida manual: Redirigimos la subida a nuestro endpoint personalizado
                    for f in e.files:
                        f.upload_url = "/api/upload"

                    print(f"DEBUG: [WEB] Redirecting upload to: {e.files[0].upload_url}")
                    
                    file_picker.upload(e.files)
                    result_text.value = "Iniciando subida web (0%)..."
                    result_text.color = "blue"
                    result_text.update()
                else:
                    # Si estamos en ESCRITORIO o MÓVIL (APK local)
                    # No necesitamos subir nada, el archivo ya está accesible localmente
                    # (Flet copia los archivos seleccionados en Android a una caché accesible)
                    file_path = e.files[0].path
                    print(f"DEBUG: [LOCAL] Archivo seleccionado: {file_path}")
                    
                    result_text.value = "Procesando imagen local..."
                    result_text.color = "blue"
                    result_text.update()
                    
                    # Llamada directa al análisis
                    try:
                        run_analysis(file_path, e.files[0].name)
                    except Exception as ex:
                        result_text.value = f"Error procesando local: {str(ex)}"
                        result_text.color = "red"
                        result_text.update()

        # on_upload_progress para feedback visual
        def on_upload_progress(e: ft.FilePickerUploadEvent):
            result_text.value = f"Subiendo... {int(e.progress * 100)}%"
            result_text.update()

        file_picker = ft.FilePicker(on_result=on_dialog_result, on_upload=on_upload_complete) # No hay on_upload_progress en esta versión de Flet wrapper simple, pero si existe en API
        # Intentamos enlazar progreso si es posible o dejamos simple
        
        self.page.overlay.append(file_picker)

        return ft.View(
            "/detection",
            controls=[
                ft.AppBar(title=ft.Text("Detección"), bgcolor="surface_variant"),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Subir Imagen de Mango", size=20),
                            ft.Row(
                                [
                                    ft.ElevatedButton("Seleccionar Foto / Cámara", icon="add_a_photo", 
                                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), padding=15, bgcolor="blue", color="white"),
                                                    on_click=lambda _: file_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=20
                            ),
                            ft.Text("Nota: Usa la opción de cámara dentro del selector si deseas tomar una foto.", size=12, color="grey", italic=True),
                            img_control,
                            toggle_btn, # Botón para ver imagen procesada
                            ft.Divider(),
                            result_text,
                            ft.Container(content=treatment_text, padding=10, bgcolor="blue_50", border_radius=5),
                            ft.ElevatedButton("Volver", on_click=lambda _: self.page.go("/dashboard")),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        scroll=ft.ScrollMode.AUTO
                    ),
                    padding=20,
                    expand=True
                )
            ]
        )

