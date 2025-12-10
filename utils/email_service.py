import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    def __init__(self):
        # Configuración por defecto (Debe ser cambiada por el usuario)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "tu_correo@gmail.com" # CAMBIAR ESTO
        self.sender_password = "tu_contraseña_de_aplicacion" # CAMBIAR ESTO

    def update_credentials(self, email, password):
        self.sender_email = email
        self.sender_password = password

    def send_email(self, recipient, subject, body):
        def _send():
            try:
                msg = MIMEMultipart()
                msg['From'] = self.sender_email
                msg['To'] = recipient
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))

                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                text = msg.as_string()
                server.sendmail(self.sender_email, recipient, text)
                server.quit()
                print(f"Correo enviado a {recipient}")
            except Exception as e:
                print(f"Error enviando correo: {e}")
            
        thread = threading.Thread(target=_send)
        thread.start()

email_service = EmailService()
