# Guía de ejecución y traspaso de M4

## Estado al 8 de septiembre de 2026

M4 — Verificación de cámara e imagen — está iniciado, pero no está completo.
La parte de software y las verificaciones con geometría analítica y archivos
sintéticos están implementadas. Faltan la captura representativa del teléfono,
las pruebas físicas con un objeto planar y la selección de una configuración
de cámara sustentada por esos resultados.

El repositorio tiene 59 pruebas automatizadas aprobadas. Los cambios iniciales
de M4 están contenidos en estos commits:

- `0798f6c feat: start camera and image verification`
- `e5defa0 feat: add video metadata inspection`

## Qué se implementó

### M4-A — Conversión de coordenadas

`src/motionlab/image_geometry.py` introduce:

- `ImageSize`, que exige ancho y alto positivos y enteros;
- `normalized_to_pixel`, que escala `x` por el ancho y `y` por el alto;
- `angle_from_normalized_points_deg`, que convierte antes de calcular el
  ángulo.

Las coordenadas se conservan como posiciones continuas. No se redondean a
índices de píxel y no se recortan al intervalo `[0, 1]`. Esto permite conservar
un landmark que el modelo reporte fuera de la imagen para que la política de
calidad se defina después, sin modificar silenciosamente el dato crudo.

Las pruebas demuestran que calcular directamente con coordenadas normalizadas
en una imagen no cuadrada puede producir un error angular material. También
verifican la recuperación de un ángulo conocido en formatos horizontal 16:9,
4:3 y vertical 9:16. Este bloque aporta evidencia para `ML-MOD-002`.

### M4-B — Imágenes sintéticas

`tests/test_synthetic_image_geometry.py` construye marcadores con geometría
conocida, codifica la imagen como PNG, la vuelve a decodificar y recupera
ángulos agudos, rectos y obtusos desde los centroides observados. Así se prueba
una ruta de imagen real, aunque todavía sin lente, perspectiva ni compresión de
video de un teléfono.

### M4-C — Inspección de video

`src/motionlab/video_metadata.py` inspecciona un archivo sin modificarlo y
genera un registro JSON con:

- nombre original, extensión, tamaño y checksum SHA-256;
- ancho y alto del primer cuadro realmente decodificado;
- conteo de cuadros y FPS nominal informados por el backend;
- duración derivada de esos dos valores;
- códec FOURCC y backend de captura;
- orientación informada por el backend;
- notas que limitan la interpretación de orientación y temporización.

El inspector se probó de extremo a extremo con un video AVI generado durante
la suite. También se verificaron archivos inexistentes o no decodificables y la
exportación JSON desde la línea de comandos.

El FPS del encabezado no demuestra que el archivo tenga cuadros igualmente
espaciados. La duración calculada tampoco sustituye la inspección de timestamps.
Una orientación de 0° puede significar cero rotación o metadatos no disponibles.
Estas limitaciones se conservan explícitamente para evitar conclusiones falsas.

## Qué no se ha demostrado todavía

M4 no contiene evidencia física sobre:

- el teléfono, lente o aplicación que se utilizarán;
- distorsión óptica, zoom digital, HDR o estabilización;
- velocidad de cuadros constante o variable;
- rotación y recorte efectivos del archivo del teléfono;
- sensibilidad a yaw, pitch, roll, altura o distancia;
- repetibilidad al desmontar y reinstalar la cámara;
- tolerancias aceptables para el montaje;
- validez de landmarks humanos o acuerdo con la referencia manual.

Por tanto, M4 aún no permite declarar una configuración de adquisición validada.

## Lo que debes preparar

Necesitas:

1. el teléfono y la aplicación de cámara que planeas usar;
2. un soporte estable o trípode;
3. una cinta métrica y, si es posible, un nivel;
4. un blanco planar rígido con al menos tres centros de alto contraste;
5. una medida independiente de las distancias y del ángulo entre esos centros;
6. una marca asimétrica que permita detectar rotaciones o reflejos;
7. un espacio donde puedas repetir posición, altura, distancia e iluminación.

No uses todavía una persona como blanco de M4. Primero debe caracterizarse el
comportamiento de cámara e imagen con geometría planar conocida.

## Primera captura representativa — M4-C

### 1. Conserva el archivo original

Crea el área privada local:

```powershell
New-Item -ItemType Directory -Path data\raw\m4 -Force
```

Coloca allí el archivo original del teléfono. No lo recortes, renombres,
transcodifiques ni envíes por una aplicación que pueda recomprimirlo. Todo
`data/raw/` está excluido de Git.

### 2. Registra lo que configuraste

Copia la plantilla versionada:

```powershell
Copy-Item docs\metrology\acquisition_record_template.yaml `
  data\raw\m4\baseline_001_acquisition.yaml
```

Completa los campos que puedas observar: teléfono, sistema operativo,
aplicación, resolución solicitada, FPS solicitado, orientación, lente, zoom,
estabilización, HDR, enfoque, exposición, balance de blancos, soporte, altura,
distancia y orientación física. Usa `null` cuando un valor no esté disponible;
no lo deduzcas visualmente.

### 3. Inspecciona el archivo

Sustituye `<video>` por el nombre real:

```powershell
.\.venv\Scripts\python.exe -m motionlab.video_metadata `
  data\raw\m4\<video> `
  --output data\raw\m4\baseline_001_metadata.json
```

No edites el JSON resultante. Si repites el comando sobre el mismo archivo, el
checksum debe permanecer idéntico.

### 4. Revisa coherencia básica

Compara el YAML y el JSON:

- resolución solicitada frente a dimensiones decodificadas;
- FPS solicitado frente a FPS nominal informado;
- orientación esperada frente a dimensiones y orientación informada;
- lente, zoom y estabilización registrados manualmente;
- nombre y checksum correspondientes al archivo original.

Una discrepancia se documenta; no se corrige alterando el archivo fuente.

## Secuencia física — M4-D

Antes de observar errores angulares, crea una copia de la plantilla para cada
condición y fija por escrito los niveles que sean realizables con tu equipo.
No definas tolerancias después de ver qué condición produjo mejores resultados.

Ejecuta esta secuencia:

1. varias capturas repetidas de la condición baseline sin mover nada;
2. cambios de una sola variable por vez: yaw, pitch, roll, altura y distancia;
3. pruebas separadas de cada lente, zoom, estabilización y modo de resolución o
   FPS que sea candidato para el protocolo;
4. una prueba de orientación y recorte con el blanco asimétrico;
5. una captura final de retorno al baseline;
6. inspección JSON y registro YAML para cada video original.

Mantén constantes el blanco, la iluminación y las variables que no estén bajo
prueba. Si algo cambia accidentalmente, anótalo; no descartes la captura sin
dejar registro.

## Qué debes entregar para continuar el análisis

Cuando completes la primera captura, proporciona:

- la ruta local exacta del video dentro de `data/raw/m4/`;
- el YAML de adquisición completado;
- el JSON generado por el inspector;
- las dimensiones físicas y el ángulo nominal del blanco;
- una descripción de cómo mediste altura, distancia, yaw, pitch y roll;
- cualquier ajuste que la aplicación no permita controlar.

Con esos insumos se podrá analizar la captura real, decidir los niveles de la
secuencia M4-D y, después de las pruebas, justificar una configuración baseline
provisional para M9 y las tolerancias que llegarán al protocolo M10.

## Comandos de comprobación

Ejecuta toda la evidencia automatizada con:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

El resultado del checkpoint documentado es:

```text
59 passed
```

Si este número cambia porque se añaden pruebas, lo importante es que toda la
suite termine sin fallos y que el nuevo resultado quede registrado.

## Condición de cierre de M4

M4 solo podrá marcarse completo cuando exista al menos un registro real de
dispositivo y video, se documenten y ejecuten las pruebas planares, se reporten
los efectos observados dentro de las condiciones ensayadas y se justifique una
configuración baseline con tolerancias sustentadas por evidencia. El cierre de
M4 no autoriza afirmaciones clínicas, anatómicas 3D ni de validez de pose humana.
