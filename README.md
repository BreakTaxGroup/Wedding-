# Invitación de boda · Idanay & Humberto

**11 de marzo de 2027 · Orange Farm, Orlando, FL**

Invitación digital hiperrealista: un sobre de papel artesanal con sello de cera en el bosque. El invitado toca el sello, la cera se rompe y de él se abre la invitación interactiva con el video de los novios de fondo.

## Estructura

| Archivo | Qué es |
| --- | --- |
| `invitacion/index.html` | Invitación completa. `#i-CODIGO` = enlace de cada invitado; `#admin` = panel de los novios |
| `invitacion/media/` | Video de fondo, save the date, sobre y sello (capas) |
| `invitacion/HIGGSFIELD.md` | Prompts para generar el sobre y la ruptura del sello en Higgsfield |
| `tools/prep_video.sh` | Endereza y recorta el video original de los novios |
| `tools/prep_sobre.py` | Borra el nombre impreso del sobre, cambia el monograma del sello y lo parte en dos |

## Paleta

| Color | Uso |
| --- | --- |
| Deep Espresso `#3A2218` | Color principal · damas y cortejo (los invitados no lo usan) |
| Beige claro `#DABFA4` | Invitados |
| Verde olivo `#565024` | Invitados |
| Olivo suave `#979364` | Invitados |
| Burdeos `#5F1216` | Invitados |
| Crema `#D4C2A8` | Papelería |

## Panel de administración (`#admin`)

- **Invitados:** nombre que aparece en el sobre, lugares, teléfono e idioma. Cada uno tiene su enlace y botón de WhatsApp.
- **Respuestas:** quién confirma, cuántas personas y su mensaje.
- **Detalles:** horarios, dirección, itinerario, fecha límite, regalos, hospedaje, historia y preguntas. Lo que se llena aparece en la invitación; lo vacío no se muestra.
