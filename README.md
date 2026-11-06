# Invitación digital de boda

Sitio de invitaciones para una boda en el bosque. Cada invitado recibe un enlace único que abre un sobre animado con su nombre; dentro está la invitación y el sitio con toda la información. Un panel de administración maneja invitados y confirmaciones.

## Paleta

| Color | Uso |
| --- | --- |
| Deep Espresso `#3A261C` | Damas y cortejo (los invitados no lo usan) |
| Burdeos `#621720` | Invitados |
| Verde Olivo `#545530` | Invitados |
| Olivo Suave `#9C9A6A` | Invitados |
| Beige Claro `#DCC6AC` | Invitados |
| Crema `#E6DAC6` | Papelería |

## Proceso

1. **El sobre**: `propuestas/01-sobres.html` (elegido: C, Papel de Bosque)
2. **La apertura**: video de Gemini procesado con `tools/process_video.py` (borra el nombre impreso, corrige el texto ilegible de la tarjeta y guarda el seguimiento para escribir el nombre de cada invitado)
3. **El sitio web**: `propuestas/invitacion.html` — réplica del sitio del video de Gemini (portada que se funde con la foto, Nuestra Historia, Ubicación, RSVP). Enlace por invitado: `#para-familia-lopez`
4. Panel de administración, enlaces únicos y confirmaciones: pendiente
