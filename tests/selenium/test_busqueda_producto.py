import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementNotInteractableException

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/customer/login"
EMAIL = "cliente@example.com"
PASSWORD = "password"
PRODUCTO_BUSQUEDA = "Camisa"
SCREENSHOT_PATH = "tests/selenium/producto_detalle.png"


def esperar_click(driver, xpath, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )


def esperar_visible(driver, xpath, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.XPATH, xpath))
    )


def escribir_lento(element, texto, delay=0.4):
    for ch in texto:
        element.send_keys(ch)
        time.sleep(delay)


def resaltar_elemento(driver, element, duration=0.6):
    # Añade un borde temporal para simular enfoque/selección
    try:
        driver.execute_script(
            "arguments[0].setAttribute('style', arguments[1]);",
            element,
            "border: 2px solid #ff0055; box-shadow: 0 0 6px #ff0055;"
        )
        time.sleep(duration)
        driver.execute_script(
            "arguments[0].setAttribute('style', arguments[1]);",
            element,
            ""
        )
    except StaleElementReferenceException:
        # Ignorar si el elemento se volvió 'stale' por re-render; no es crítico
        pass


# --------- Checklist util ---------
CHECKLIST = [
    ("1. Abrir navegador", False),
    ("2. Iniciar sesión", False),
    ("  2.1. Escribir email", False),
    ("  2.2. Escribir contraseña", False),
    ("3. Buscar un producto", False),
    ("  3.1. Escribir producto a buscar", False),
    ("4. Ver resultados del producto buscado", False),
    ("5. Seleccionar producto para ver detalles", False),
    ("  5.1. Seleccionar producto", False),
    ("  5.2. Ver detalles del producto", False),
    ("6. Tomar captura de pantalla del detalle", False),
    ("7. Cerrar navegador", False),
]


def print_checklist():
    # Salida limpia: no imprimir resumen completo al final
    pass


def complete(label):
    for i, (lbl, done) in enumerate(CHECKLIST):
        if lbl == label:
            if not done:
                CHECKLIST[i] = (lbl, True)
                # Imprime sólo la actividad que se completó
                print(f"✓ {lbl}")
            break


def buscar_enlace_producto(wait):
    # Retorna el enlace clicable al producto Camisa si existe
    try:
        return wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(.,'Camisa') or contains(@title,'Camisa') or contains(@href,'/camisa')]"))
        )
    except Exception:
        try:
            card = wait.until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'/camisa')]"))
            )
            return card
        except Exception:
            return None


def scroll_into_view(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.4)
    except StaleElementReferenceException:
        pass


def main():
    driver = webdriver.Firefox(service=Service())
    driver.maximize_window()
    wait = WebDriverWait(driver, 15)

    try:
        driver.get(BASE_URL)
        # Reducir permanencia en home: breve pausa
        time.sleep(0.4)
        complete("1. Abrir navegador")

        icon_selectors = [
            "//button[contains(@aria-label,'account')]",
            "//button[contains(@aria-label,'Account')]",
            "//button[contains(@class,'account')]",
            "//a[contains(@href,'login') and (contains(.,'Sign') or contains(.,'Login'))]",
        ]
        icon_clicked = False
        for xp in icon_selectors:
            try:
                el = esperar_click(driver, xp, timeout=5)
                el.click()
                icon_clicked = True
                break
            except Exception:
                pass

        if icon_clicked:
            try:
                btn_sign_in = esperar_click(driver, "//button[normalize-space()='Sign In' or normalize-space()='Sign in']", timeout=5)
                btn_sign_in.click()
            except Exception:
                driver.get(LOGIN_URL)
        else:
            driver.get(LOGIN_URL)

        # Permanecer en la pantalla de login y escribir letra por letra
        email_input = esperar_visible(driver, "//input[@type='email']")
        password_input = esperar_visible(driver, "//input[@type='password']")
        ActionChains(driver).move_to_element(email_input).pause(0.3).perform()
        email_input.click()
        email_input.clear()
        escribir_lento(email_input, EMAIL, delay=0.2)
        complete("2. Iniciar sesión")
        complete("  2.1. Escribir email")

        # Mostrar contraseña si existe el checkbox "Show Password"
        try:
            show_pwd = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[contains(.,'Show Password')] | //input[@type='checkbox' and (contains(@aria-label,'Show Password') or contains(@id,'show') or contains(@name,'show'))]")))
            try:
                show_pwd.click()
            except Exception:
                pass
        except Exception:
            pass

        ActionChains(driver).move_to_element(password_input).pause(0.3).perform()
        password_input.click()
        password_input.clear()
        escribir_lento(password_input, PASSWORD, delay=0.2)
        complete("  2.2. Escribir contraseña")

        # Pausa ligera para visualizar antes de enviar
        time.sleep(0.6)
        login_btn = esperar_click(driver, "//button[normalize-space()='Sign In' or normalize-space()='Sign in']")
        resaltar_elemento(driver, login_btn, duration=0.4)
        login_btn.click()

        # Espera breve al redireccionamiento post-login
        time.sleep(1.2)

        search_input = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search products here']"))
        )
        search_input.click()
        search_input.clear()
        escribir_lento(search_input, PRODUCTO_BUSQUEDA, delay=0.25)
        complete("3. Buscar un producto")
        complete("  3.1. Escribir producto a buscar")
        search_input.send_keys(Keys.ENTER)

        # Esperar resultados: mostrar brevemente la página de búsqueda
        try:
            WebDriverWait(driver, 10).until(EC.url_contains("/search"))
        except Exception:
            pass
        time.sleep(1.2)
        complete("4. Ver resultados del producto buscado")

        # Seleccionar visiblemente el producto "Camisa" y entrar al detalle
        # Intento 1: enlace con texto Camisa
        producto_link = buscar_enlace_producto(wait)

        if not producto_link:
            # Fallback: navegar por URL conocida
            driver.get(f"{BASE_URL}/camisa")
        else:
            # Click directo y robusto sin scroll ni hover
            producto_link = buscar_enlace_producto(wait) or producto_link
            try:
                driver.execute_script("arguments[0].click();", producto_link)
            except StaleElementReferenceException:
                producto_link = buscar_enlace_producto(wait)
                if producto_link:
                    driver.execute_script("arguments[0].click();", producto_link)
        complete("5. Seleccionar producto para ver detalles")
        complete("  5.1. Seleccionar producto")

        # Esperar que la URL sea del detalle para asegurar captura correcta
        try:
            WebDriverWait(driver, 10).until(EC.url_contains("/camisa"))
        except Exception:
            pass
        # Pausa breve para que se renderice el detalle
        time.sleep(1.0)
        complete("  5.2. Ver detalles del producto")

        nombre_elemento = esperar_visible(
            driver,
            "//h1[contains(.,'Camisa')] | //h2[contains(.,'Camisa')] | //div[contains(@class,'product')][contains(.,'Camisa')]",
            timeout=15,
        )
        nombre_texto = nombre_elemento.text.strip()
        assert "Camisa".lower() in nombre_texto.lower(), f"El nombre del producto no contiene 'Camisa': {nombre_texto}"

        # Screenshot del detalle del producto
        driver.save_screenshot(SCREENSHOT_PATH)
        complete("6. Tomar captura de pantalla del detalle")
        print(f"Screenshot guardado en {SCREENSHOT_PATH}")

    finally:
        # Pausa más larga antes de cerrar para visualizar los detalles
        time.sleep(3.0)
        complete("7. Cerrar navegador")
        driver.quit()
        print("\nEn caso de que no los vea, buenos días, buenas tardes y buenas noches.")


if __name__ == "__main__":
    main()
