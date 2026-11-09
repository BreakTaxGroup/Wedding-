# Invitación de boda · Idanay & Humberto

**11 de marzo de 2027 · Orange Farm, Orlando, FL**

**En línea:** https://idanay-y-humberto.vercel.app

Invitación digital hiperrealista: un sobre de papel artesanal con sello de cera sobre un tronco en el bosque. El invitado toca el sello y un video generado en Higgsfield lo abre: la cera se rompe, la solapa se levanta y la tarjeta deep espresso sube hasta llenar la pantalla y se convierte en la invitación, con el video de los novios de fondo y su música.

## Dónde vive

| Pieza | Dónde | Cuenta |
| --- | --- | --- |
| Sitio | Vercel, proyecto `idanay-y-humberto` (plan Hobby, gratis) | humbertovilliva@gmail.com |
| Base de datos | Supabase, proyecto `boda-idanay-humberto` (us-east-1, plan Free) | humbertovilliva@gmail.com |
| Visita diaria | Cron de Vercel → `/api/keepalive`, para que Supabase no se pause | — |

## Estructura

| Archivo | Qué es |
| --- | --- |
| `invitacion/index.html` | Invitación completa. `/#i-CODIGO` = enlace de cada invitado. `/#admin` = panel de los novios (pide la clave) |
| `invitacion/media/` | Apertura (Higgsfield), loop de espera, tarjeta, música, video de fondo, save the date, imagen para WhatsApp e íconos |
| `invitacion/api/keepalive.js`, `invitacion/vercel.json` | Visita diaria a la base de datos y cabeceras del sitio |
| `supabase/schema.sql` | Tablas y funciones de la base de datos (sin la clave) |
| `invitacion/HIGGSFIELD.md` | Cómo se generó la apertura en Higgsfield (modelo, prompt, IDs) |
| `tools/deploy_vercel.sh` | Publica `invitacion/` en Vercel |
| `tools/prep_video.sh` | Endereza y recorta el video original de los novios |
| `tools/prep_apertura.sh` | Corta el video de Higgsfield en loop de espera + apertura, saca la tarjeta y la música |

## Paleta

| Color | Uso |
| --- | --- |
| Deep Espresso `#3A2218` | Color principal · damas y cortejo (los invitados no lo usan) |
| Beige claro `#DABFA4` | Invitados |
| Verde olivo `#565024` | Invitados |
| Olivo suave `#979364` | Invitados |
| Burdeos `#5F1216` | Invitados |
| Crema `#D4C2A8` | Papelería |

## Panel de administración (privado)

- **Agregar invitación:** persona, pareja o familia. El nombre se escribe a mano en el sobre ("Carlos & María", "Familia Pérez"), la invitación les habla de tú o de ustedes según el tipo, y pueden llevar un mensaje personal que aparece como una carta.
- **Agregar varias a la vez:** pegar la lista, una invitación por línea (`Carlos Pérez`, `Ana López + 1`, `Carlos y María`, `Familia Pérez, 4`, `… | 407 555 0123`, `… | en`).
- **Enviar:** cada invitación tiene su enlace único, botón de WhatsApp con un mensaje personalizado, copiar mensaje y copiar enlace. Al enviarla queda marcada como enviada.
- **Respuestas:** quiénes asisten (por nombre), alergias y mensaje. "Copiar lista para Excel o Sheets" exporta todo.
- **Detalles:** horarios, dirección, itinerario, fecha límite, regalos, hospedaje, historia y preguntas.

### Enlaces de invitado

`https://idanay-y-humberto.vercel.app/#i-CODIGO` (8 caracteres). La invitación lee de la base de datos solo lo de ese invitado (nombre del sobre, tipo, lugares, idioma y mensaje), así que si los novios lo editan después de enviarlo, el invitado ve el cambio sin reenviar el enlace. La lista completa (con teléfonos) solo se lee con la clave de los novios.
