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
2. **La apertura**: video de Gemini (sobre C) procesado con `tools/process_video.py`: sin el nombre impreso, con el texto real en la tarjeta y el nombre de cada invitado seguido cuadro por cuadro
3. **El sitio web**: `propuestas/invitacion.html` — la tarjeta del video se funde con el sitio (estilo Gemini). Enlace por invitado: `#para-familia-lopez`
4. Panel de administración, enlaces únicos y confirmaciones: pendiente
