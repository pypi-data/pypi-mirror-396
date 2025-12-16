# 🐍 SerpentUI v2.0

**Crea Apps de Escritorio Modernas con Solo Python - ¡Solo Dale Click a Run!**

SerpentUI v2.0 es el framework de Python más fácil para crear aplicaciones de escritorio con interfaces modernas. **Escribe solo Python**, dale click a Run, ¡y tu app se abre automáticamente en una ventana nativa!

## ✨ Lo Nuevo en v2.0

- 🖥️ **Flask + WebView integrados** - Apps nativas automáticas
- ⚡ **Un solo click para ejecutar** - Solo `app.run()` y listo!
- 🎯 **API súper simplificada** - Menos código, más rápido
- 🚀 **Helper functions** - `Row()`, `Column()`, `Page()` para UI instantáneas
- 🔥 **Quick App mode** - Crea apps en 5 líneas de código

## 🚀 Instalación Rápida

```bash
pip install serpentui flask pywebview
```

O todo junto:
```bash
pip install serpentui[full]
```

## ⚡ Quick Start - ¡5 Líneas de Código!

```python
from serpentui import *

app = SerpentApp(title="Mi App")
app.set_root(Page(Heading("¡Hola!"), Button("Click")))
app.run()  # ¡Se abre automáticamente! 🎉
```

**¡Eso es todo!** Dale Run y tu app se abre en una ventana nativa.

## 📱 Modos de Ejecución

### 1. Desktop Mode (Recomendado) 🖥️
```python
app.run()  # Ventana nativa automática
```

### 2. Browser Mode 🌐
```python
app.run(mode='browser')  # Abre en navegador
```

### 3. Server Mode 🌍
```python
app.run(mode='server', port=5000)  # Solo servidor Flask
```

## 💡 Ejemplos Súper Fáciles

### Ejemplo 1: Dashboard en 15 Líneas

```python
from serpentui import *

app = SerpentApp(title="Dashboard", width=1200, height=800)

ui = Page(
    Heading("Mi Dashboard 📊", level=1),
    
    Row(
        Card(children=[CardBody(children=[Heading("1,234"), Text("Usuarios")])]),
        Card(children=[CardBody(children=[Heading("$45K"), Text("Ventas")])]),
        Card(children=[CardBody(children=[Heading("89%"), Text("Éxito")])]),
        gap=4
    ),
    
    Terminal(height="300px")
)

app.set_root(ui)
app.run()  # ¡Click y listo!
```

### Ejemplo 2: Formulario de Login

```python
from serpentui import *

app = SerpentApp(title="Login")

ui = Page(
    Card(children=[
        CardHeader(children=[Heading("Iniciar Sesión", level=2)]),
        CardBody(children=[
            Input(label="Email", placeholder="tu@email.com", type="email"),
            Input(label="Password", placeholder="••••••••", type="password"),
            Button("Entrar", color="primary")
        ])
    ], className="max-w-md mx-auto mt-20")
)

app.set_root(ui)
app.run()
```

### Ejemplo 3: Quick App (Lo Más Rápido)

```python
from serpentui import *

def mi_ui():
    return Page(
        Heading("Super Fácil!", level=1),
        Button("Increíble", color="success"),
        Terminal()
    )

quick_app(mi_ui, title="Quick App")  # Una sola línea!
```

## 🌀 Compatibilidad estilo Wails (Python puro)

Si vienes de [Wails](https://wails.io/docs/introduction) y quieres la misma simplicidad pero **sin escribir HTML ni JavaScript**, puedes usar las APIs Wails-like incluidas:

```python
from serpentui import WailsApp, WailsWindow, WailsMenu, MenuItem, Page, Heading, Button

# Definir un menú nativo 100% Python
file_menu = WailsMenu().add_item(MenuItem("Salir", action=lambda: print("Bye!")))

# Construir la ventana principal con componentes SerpentUI
main_window = (
    WailsWindow(title="App tipo Wails", width=1100, height=700)
    .set_content(
        Page(
            Heading("Hola desde SerpentUI"),
            Button("Click"),
        )
    )
)

app = WailsApp(name="Mi App Wails en Python")
app.add_menu(file_menu).add_window(main_window)
app.run()  # Abre ventana nativa; no hay HTML que tocar
```

Esto replica la ergonomía de Wails: ventanas declaradas en Python, menús y diálogos (`WailsDialog.alert`, `WailsDialog.confirm`, `WailsNotification.show`) listos para usar y sin plantillas HTML.

## 🎨 Componentes Disponibles (40+)

### Layout Helpers (NUEVO)
```python
Row(componente1, componente2, componente3)      # Fila horizontal
Column(componente1, componente2, componente3)   # Columna vertical
Page(componente1, componente2)                  # Página con contenedor
```

### Botones & Entrada
- `Button(text, color, variant, size)` - Botones modernos
- `Input(label, placeholder, type)` - Campos de entrada
- `Switch(isSelected)` - Interruptores

### Tarjetas
- `Card()` / `CardHeader()` / `CardBody()` / `CardFooter()`

### Navegación
- `Navbar()` / `NavbarBrand()` / `NavbarContent()` / `NavbarItem()`

### Layout
- `Container()` / `Grid()` / `Flex()` / `Box()` / `Divider()` / `Spacer()`

### Datos
- `Table(columns, rows)` - Tablas de datos
- `Progress(value, color)` - Barras de progreso
- `Chip()` / `Avatar()` / `Spinner()`

### Texto
- `Text()` / `Heading(level)` / `Link()` / `Image()`

### Modales
- `Modal()` / `ModalContent()` / `ModalHeader()` / `ModalBody()` / `ModalFooter()`

### Especial
- `Terminal(title, height)` ⚡ - Terminal interactiva

## 🎯 Props Simplificadas

Todos los componentes tienen valores por defecto inteligentes:

```python
# Antes (otros frameworks)
Button(text="Click", color="primary", variant="solid", size="md", disabled=False)

# Ahora (SerpentUI v2.0)
Button("Click")  # color="primary" por defecto!

# Solo especifica lo que necesitas
Button("Click", color="success")
```

## 🔥 Características Avanzadas

### Personalización de Ventana
```python
app = SerpentApp(
    title="Mi App",
    theme="dark",      # o "light"
    width=1400,
    height=900,
    resizable=True
)
```

### Múltiples Modos
```python
app.run()                           # Desktop (ventana nativa)
app.run(mode='browser')             # Browser
app.run(mode='server', port=8000)   # Solo servidor
```

### Guardar como HTML
```python
app.save_html("mi_app.html")  # Exportar a HTML standalone
```

## 📦 Estructura de Proyecto

```
mi-proyecto/
├── app.py              # Tu aplicación principal
├── requirements.txt    # flask, pywebview
└── README.md
```

**requirements.txt:**
```txt
flask>=2.0.0
pywebview>=4.0.0
```

## 🎨 Temas y Colores

### Colores Disponibles
- `primary` (azul), `secondary` (púrpura), `success` (verde)
- `warning` (amarillo), `danger` (rojo), `default` (gris)

### Tamaños
- `sm` (pequeño), `md` (mediano), `lg` (grande), `xl` (extra grande)

### Variantes
- `solid`, `bordered`, `light`, `flat`, `faded`, `shadow`

## 🏗️ Ejemplos Completos

### App de Tareas

```python
from serpentui import *

app = SerpentApp(title="Task Manager")

ui = Page(
    Heading("📝 Mis Tareas", level=1, className="mb-4"),
    
    Card(children=[
        CardBody(children=[
            Input(placeholder="Nueva tarea...", className="mb-2"),
            Button("Agregar Tarea", color="primary")
        ])
    ], className="mb-4"),
    
    Card(children=[
        CardHeader(children=["Tareas Pendientes"]),
        CardBody(children=[
            Row(Chip("Comprar leche"), Button("✓", size="sm"), className="mb-2"),
            Row(Chip("Llamar a Juan"), Button("✓", size="sm"), className="mb-2"),
            Row(Chip("Revisar email"), Button("✓", size="sm"))
        ])
    ])
)

app.set_root(ui)
app.run()
```

### Monitor del Sistema

```python
from serpentui import *

app = SerpentApp(title="System Monitor")

ui = Page(
    Heading("💻 Monitor del Sistema", level=1),
    
    Grid(cols=2, gap=4, children=[
        Card(children=[
            CardHeader(children=["CPU"]),
            CardBody(children=[
                Progress(value=45, color="success"),
                Text("45% en uso")
            ])
        ]),
        Card(children=[
            CardHeader(children=["RAM"]),
            CardBody(children=[
                Progress(value=72, color="warning"),
                Text("72% en uso")
            ])
        ])
    ], className="mb-4"),
    
    Terminal(title="System Logs", height="400px")
)

app.set_root(ui)
app.run()
```

## 🚀 Despliegue

### Como App de Escritorio
Tu app ya funciona como app de escritorio con `app.run()`. Para distribuirla:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed app.py
```

### Como App Web
```python
app.run(mode='server', port=5000)
# Despliega en Heroku, Railway, etc.
```

## 🧪 Testing

```bash
# Instalar deps de desarrollo
pip install pytest black mypy

# Ejecutar tests
pytest

# Formatear código
black .

# Verificar tipos
mypy serpentui
```

## 📖 Documentación Completa

- 📚 [Guía Completa](https://docs.serpentui.dev)
- 🎓 [Tutoriales](https://docs.serpentui.dev/tutorials)
- 📘 [API Reference](https://docs.serpentui.dev/api)
- 💡 [Ejemplos](https://github.com/serpentui/examples)

## ❓ FAQ

**P: ¿Necesito saber JavaScript?**  
R: ¡No! Solo Python puro.

**P: ¿Funciona en Windows/Mac/Linux?**  
R: ¡Sí! Multiplataforma total.

**P: ¿Puedo hacer apps grandes?**  
R: ¡Absolutamente! Flask maneja todo el backend.

**P: ¿Cómo manejo eventos de botones?**  
R: Usa Flask routes o callbacks (próximamente).

## 🎯 Comparación con Otros Frameworks

| Feature | SerpentUI v2.0 | Tkinter | PyQt | Electron |
|---------|---------------|---------|------|----------|
| Solo Python | ✅ | ✅ | ✅ | ❌ |
| UI Moderna | ✅ | ❌ | ⚠️ | ✅ |
| Fácil de usar | ✅ | ⚠️ | ❌ | ⚠️ |
| Tamaño pequeño | ✅ | ✅ | ❌ | ❌ |
| Web + Desktop | ✅ | ❌ | ❌ | ✅ |

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea tu rama (`git checkout -b feature/amazing`)
3. Commit cambios (`git commit -m 'Add feature'`)
4. Push (`git push origin feature/amazing`)
5. Abre un Pull Request

## 📄 Licencia

MIT License - usa SerpentUI como quieras!

## 🙏 Agradecimientos

- [React](https://react.dev/) - UI library
- [NextUI](https://nextui.org/) - Componentes hermosos
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [PyWebView](https://pywebview.flowrl.com/) - Ventanas nativas
- Comunidad Python 🐍

## 💬 Comunidad

- 📧 Email: hello@serpentui.dev
- 🐛 Issues: [GitHub](https://github.com/serpentui/serpentui/issues)
- 💬 Discord: [Join us](https://discord.gg/serpentui)
- 🐦 Twitter: [@serpentui](https://twitter.com/serpentui)

## 🌟 Proyectos Hechos con SerpentUI

- [Task Manager Pro](https://github.com/user/taskpro)
- [System Monitor](https://github.com/user/sysmon)
- [Notes App](https://github.com/user/notes)

¿Hiciste algo con SerpentUI? [¡Compártelo!](https://github.com/serpentui/serpentui/discussions)

---

**Hecho con ❤️ y 🐍 por la comunidad**

**SerpentUI v2.0** - Porque crear UIs debería ser tan fácil como escribir Python 🚀
