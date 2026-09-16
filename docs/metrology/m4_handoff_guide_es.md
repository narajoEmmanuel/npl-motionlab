# Guía de traspaso de M4, estado histórico

## Estado actual

**M4 está cerrado bajo el alcance Core simplificado adoptado el 16 de septiembre
de 2026.**

Este archivo ya no es una lista de tareas pendientes para poder avanzar. Se
conserva como guía histórica de cómo se construyó la evidencia M4 y como punto
de referencia para reproducir o extender ese trabajo en el futuro.

La decisión vigente de alcance está en:

- [`../roadmap.md`](../roadmap.md)
- [`../decisions/ADR-0003-simplified-core-scope.md`](../decisions/ADR-0003-simplified-core-scope.md)
- [`camera_image_verification.md`](camera_image_verification.md)

## Evidencia M4 que se conserva

El repositorio ya contiene:

- conversión verificada de coordenadas normalizadas a píxeles;
- pruebas de geometría con imágenes sintéticas;
- inspección de video y hashing de archivos fuente;
- una adquisición real `baseline_001`;
- cuatro digitalizaciones manuales del primer cuadro de referencia;
- una secuencia física M4-D de siete capturas;
- análisis center-versus-right;
- una decisión provisional de mantener el sujeto o blanco centrado
  horizontalmente bajo el setup Core.

Consulta:

- [`baseline_001_readiness.md`](baseline_001_readiness.md)
- [`m4d01_registration.md`](m4d01_registration.md)
- [`m4d01_results.md`](m4d01_results.md)

## Qué significan esos resultados

M4 demuestra comportamiento de software e imagen dentro de las condiciones
ensayadas. No demuestra una calibración universal de cámara.

La secuencia M4-D apoya el uso de encuadre horizontal centrado para el siguiente
workflow controlado. No permite extender esa conclusión a otros teléfonos,
lentes, posiciones de cámara o escenarios.

## Configuración práctica que pasa al Core

Para los siguientes milestones se mantendrá, en la medida práctica:

1. el mismo smartphone;
2. el mismo modo de cámara/lente del baseline escogido;
3. la misma orientación;
4. el mismo tipo de soporte;
5. altura y distancia aproximadamente consistentes;
6. vista aproximadamente sagital;
7. sujeto centrado horizontalmente;
8. iluminación y zona de captura razonablemente consistentes;
9. archivo original privado sin recomprimir;
10. checksum, dimensiones decodificadas y metadatos relevantes registrados.

No se necesitan tolerancias numéricas completas para cada variable antes de
continuar.

## Trabajo M4 que pasa a futuro, no a la ruta crítica

No es necesario ejecutar ahora:

- barridos de yaw, pitch o roll;
- múltiples alturas o distancias;
- comparación de todos los lentes;
- calibración intrínseca completa;
- mapa de distorsión de lente;
- experimentos factoriales con HDR o estabilización;
- repetibilidad de desmontaje y remontaje;
- tolerancias universales de montaje;
- caracterización general de múltiples smartphones.

Estas extensiones solo deben retomarse si aparece un problema concreto durante
la integración o si más adelante se decide estudiar robustez de forma explícita.

## Herramientas M4 retenidas

Los siguientes componentes no se eliminan porque siguen teniendo valor para
trazabilidad, pruebas o futuras extensiones:

- `src/motionlab/image_geometry.py`
- `src/motionlab/video_metadata.py`
- `scripts/manual_digitize_m4.py`
- `scripts/register_m4d01.py`
- `scripts/digitize_m4d01_batch.py`
- `scripts/analyze_m4d01.py`
- `docs/metrology/acquisition_record_template.yaml`

No forman una obligación de seguir haciendo experimentos de cámara.

## Siguiente paso vigente

El siguiente milestone es **M5, Sports2D Integration**.

La prioridad ahora es integrar una única versión/configuración de Sports2D,
obtener landmarks de cadera, rodilla y tobillo en píxeles, mapearlos a
MotionLab y dejar que la geometría ya verificada de MotionLab calcule el ángulo
autoritativo del proyecto.

No se inicia una nueva campaña de cámara antes de M5.
