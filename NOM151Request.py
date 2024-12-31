import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import hashlib
import base64
import os
import requests #pip install requests
import json
import zipfile
from tkinter.font import Font
from PIL import Image, ImageTk  #pip install pillow
# Variables globales, ajustar conforme necesario
#GlobalUrl = "https://app.com/"
GlobalUrl = "https://app-test.com/"#url para pruebas
DirArchivos = "C:/ArchivosGenerados/"#Carpeta donde se generaran los archivos
# Obtener la ruta de la carpeta actual donde se encuentra el script
current_dir = os.path.dirname(os.path.abspath(__file__))
TokenFile = os.path.join(DirArchivos, "Token.txt")

if not os.path.exists(DirArchivos):# Crear directorio para los archivos si no exite alguno
    os.makedirs(DirArchivos)
    
def select_pdf_and_hash():#Seleccciona PDF y le pide a la función generate_sha256 que lo convierta
    file_path = filedialog.askopenfilename(filetypes=[("Archivos PDF", "*.pdf")])
    if file_path:
        hash_result = generate_sha256(file_path)
        if hash_result:
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            messagebox.showinfo("Hash Generado", f"Hash SHA-256:\n{hash_result}")
            request_nom151(hash_result,file_name)
            request_timestamp(hash_result,file_name)         
             # Crear lista de archivos generados
            nom151_txt = os.path.join(DirArchivos, f"{file_name}-NOM151.txt")
            timestamp_txt = os.path.join(DirArchivos, f"{file_name}-Timestamp.txt")
            nom151_pdf = os.path.join(DirArchivos, f"{file_name}-NOM151.pdf")
            timestamp_pdf = os.path.join(DirArchivos, f"{file_name}-Timestamp.pdf")
            # Verificar si todos los archivos existen
            if all(os.path.exists(f) for f in [nom151_txt, timestamp_txt, nom151_pdf, timestamp_pdf]):
                zip_file_path = os.path.join(DirArchivos, f"{file_name}.zip")
                with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                    zipf.write(nom151_txt, os.path.basename(nom151_txt))
                    zipf.write(timestamp_txt, os.path.basename(timestamp_txt))
                    zipf.write(nom151_pdf, os.path.basename(nom151_pdf))
                    zipf.write(timestamp_pdf, os.path.basename(timestamp_pdf))       
                messagebox.showinfo("Éxito", f"Archivos comprimidos en: {zip_file_path}")
                os.remove(nom151_txt)
                os.remove(timestamp_txt)
                os.remove(nom151_pdf)
                os.remove(timestamp_pdf)
            else:
                messagebox.showerror("Error", "No se pudieron encontrar todos los archivos generados para comprimir.")

def generate_sha256(file_path):
    try:
        with open(file_path, "rb") as file:
            file_data = file.read()
        return hashlib.sha256(file_data).hexdigest()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el hash: {e}")
        return None

def base64_to_pdf(base64_string, fileName):
    try:
        output_file = os.path.join(DirArchivos, fileName + ".pdf")
        pdf_data = base64.b64decode(base64_string)
        with open(output_file, 'wb') as pdf_file:
            pdf_file.write(pdf_data)
        full_path = os.path.abspath(output_file)
        messagebox.showinfo("Éxito", f"Archivo PDF guardado exitosamente en: {full_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al convertir base64 a PDF: {e}")

def request_nom151(hash,fileName): 
    token_file = os.path.join(DirArchivos + "Token.txt")
    FILE= fileName +"-NOM151"
    output_file = os.path.join(DirArchivos, FILE + ".txt")
    url = GlobalUrl+"/nom-hash"#Configurar segun a donde se ncesite apuntar
    if not os.path.exists(token_file):
        messagebox.showerror("Error", f"El archivo {token_file} no se encuentra en la carpeta actual.")
        return
    try:  
        with open(token_file, "r") as file:# Leer el token desde el archivo
            token = file.read().strip()
        if not token.startswith("Bearer "):
            messagebox.showerror("Error", "El token en el archivo no es válido.")
            return
        headers = {        # Configurar el entorno con el token y otros parámetros
            "Authorization": token,  # "Bearer eyask3o2..."
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        data = {
            "nom_hash": hash
        }
        response = requests.post(url, json=data, headers=headers)# Realizar la solicitud POST con la libreria request
        if response.status_code == 200:         # Imprimir el resultado
            with open(output_file, "w", encoding="utf-8") as output:
                output.write(response.text)
            messagebox.showinfo(" Resultado guardado en: ", output_file)
            response_data = json.loads(response.text)# Cargar el JSON desde la respuesta
            pdf_file_content = response_data.get("response", {}).get("pdfFile", None)# Obtener el contenido de pdfFile
            if pdf_file_content:
                base64_to_pdf(pdf_file_content, FILE)
            else:
                messagebox.showerror("Error", "No se encontró el atributo 'pdfFile' en la respuesta.")
                return None
        else:
            print(f"Error {response.status_code}: {response.text}")
    except requests.RequestException as e:# Manejar errores de solicitud HTTP  
        messagebox.showerror("Error", f"Error en la solicitud HTTP: {str(e)}")    
    except Exception as e:# Manejar otros errores generales  
        messagebox.showerror("Error", f"Se produjo un error: {str(e)}")

def request_timestamp(hash,fileName):
    token_file = os.path.join(DirArchivos + "Token.txt")
    FILE= fileName +"-Timestamp"
    output_file = os.path.join(DirArchivos, FILE + ".txt")
    url = GlobalUrl+"/tsa-hash" 
    if not os.path.exists(token_file):
        messagebox.showerror("Error", f"El archivo {token_file} no se encuentra en la carpeta especificada.")
        return
    try:  
        with open(token_file, "r") as file:# Leer el token desde el archivo
            token = file.read().strip()
        if not token.startswith("Bearer "):
            messagebox.showerror("Error", "El token en el archivo no es válido.")
            return
        headers = {        # Configurar el entorno con el token y otros parámetros
            "Authorization": token,  # "Bearer eyask3o2..."
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        data = {
            "tsa_hash": hash
        }
        response = requests.post(url, json=data, headers=headers)# Realizar la solicitud POST con la libreria request
        if response.status_code == 200:         # Imprimir el resultado
            with open(output_file, "w", encoding="utf-8") as output:
                output.write(response.text)
            messagebox.showinfo(" Resultado guardado en: ", output_file)
            response_data = json.loads(response.text)# Cargar el JSON desde la respuesta
            pdf_file_content = response_data.get("response", {}).get("pdfFile", None)# Obtener el contenido de pdfFile
            if pdf_file_content:
                base64_to_pdf(pdf_file_content, FILE)
            else:
                messagebox.showerror("Error", "No se encontró el atributo 'pdfFile' en la respuesta.")
                return None
        else:
            print(f"Error {response.status_code}: {response.text}")
    except requests.RequestException as e:# Manejar errores de solicitud HTTP  
        messagebox.showerror("Error", f"Error en la solicitud HTTP: {str(e)}")    
    except Exception as e:# Manejar otros errores generales  
        messagebox.showerror("Error", f"Se produjo un error: {str(e)}")
        
def update_token():# Función para actualizar el archivo Token.txt
    new_token = simpledialog.askstring("Actualizar Token", "Pega el nuevo token aquí:")
    if new_token:
        if not new_token.startswith("Bearer "): # Asegurar que el token comience con "Bearer "
            new_token = "Bearer " + new_token.strip()
        with open(TokenFile, "w") as token_file:
            token_file.write(new_token.strip())
        messagebox.showinfo("Éxito", f"El archivo Token.txt se ha actualizado correctamente en {TokenFile}.")
    else:
        messagebox.showerror("Error", "No se ingresó ningún token.")
        
def on_enter(e, button, hover_bg, hover_fg):
    button["bg"] = hover_bg
    button["fg"] = hover_fg

def on_leave(e, button, normal_bg, normal_fg):
    button["bg"] = normal_bg
    button["fg"] = normal_fg

root = tk.Tk()#Ventana principal
root.title("Gestor de solicitudes de NOM-151")
root.geometry("700x500")
root.configure(bg="#f4f4f4") 
logo_path = os.path.join(current_dir, "logo.png")# Agregar logo y construir la ruta del logo
try:  
    logo_image = Image.open(logo_path)# Cargar y redimensionar el logo
    logo_image = logo_image.resize((160,60), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(root, image=logo_photo, bg="#f4f4f4")# Mostrar el logo en la ventana
    logo_label.image = logo_photo  # Necesario para evitar que se recolecte el garbage
    logo_label.pack(pady=10)
except Exception as e:
    print(f"Error al cargar la imagen: {e}")
title_font = Font(family="Helvetica", size=16, weight="bold")# Título con estilo
title_label = tk.Label(root, text="Haga clic y seleccione un pdf valido", font=title_font, bg="#f4f4f4", fg="#333")
title_label.pack(pady=10)

button_font = Font(family="Helvetica", size=12)# Boton para nom 151
btn_nom151 = tk.Button(
    root, 
    text="Request de NOM-151", 
    command=select_pdf_and_hash,
    font=button_font, 
    bg="#4CAF50", 
    fg="white", 
    activebackground="#45a049", 
    relief="flat"
)
btn_nom151.pack(pady=10)
btn_nom151.bind("<Enter>", lambda e: on_enter(e, btn_nom151, hover_bg="#66BB6A", hover_fg="black"))
btn_nom151.bind("<Leave>", lambda e: on_leave(e, btn_nom151, normal_bg="#4CAF50", normal_fg="white"))
info_font = Font(family="Helvetica", size=10)# Texto explicativo para el botón de token
info_text = tk.Text(
    root, 
    font=info_font, 
    bg="#f4f4f4", 
    fg="#555", 
    wrap="word", 
    height=12, 
    width=60, 
    borderwidth=0
)
info_text.insert("1.0", 
    "Unicamente actualizar token si:\n"
    "-El archivo token.txt desaparecio de la carpeta archivos generados\n"
    "-El token anterior no funciona o ha sido actualizado\n"
    "-Es la primera vez que se instala el programa en esta pc\n"
    "Para actualizar solo es necesario copiar el token proporcionado por el proveedor y pegarlo dentro del recuadro, una vez realizado un mensaje aparecera si se actualizo correctamente.\n"
    "Si este proceso no funciona o no permite timbrar con el token actualizado contacte al administrador."
)
info_text.tag_configure("red", foreground="red", justify="left")
info_text.tag_add(
    "red", 
    "0.0",  
    "4.end"   
)
info_text.configure(state="disabled")# Deshabilitar la edición del widget
info_text.pack(pady=10)# Mostrar el widget Text

btn_token = tk.Button(
    root, 
    text="Actualizar Token", 
    command=update_token,
    font=button_font, 
    bg="#2196F3", 
    fg="white", 
    activebackground="#1976D2", 
    relief="flat"
)
btn_token.pack(pady=10)
btn_token.bind("<Enter>", lambda e: on_enter(e, btn_token, hover_bg="#64B5F6", hover_fg="black"))
btn_token.bind("<Leave>", lambda e: on_leave(e, btn_token, normal_bg="#2196F3", normal_fg="white"))

root.mainloop()# Iniciar el bucle de la interfaz gráfica
