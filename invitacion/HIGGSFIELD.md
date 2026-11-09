# Higgsfield: the opening

The opening is a video generated in Higgsfield (Seedance 2.0, 9:16, 1080p, 8 s, with audio) from the couple's envelope photo, plus a final frame of the deep espresso card made with GPT Image 2.6.

- Start image: the envelope on the stump with the "I&H" seal (media `1828f2b5-62a6-41c1-9ca7-41ccf307a508`)
- Chosen video: job `dda4d8a7-b7ad-4f20-a2ce-365794e8091d` (Seedance 2.0, start image only)
- Alternatives generated: `6499323f…` (Kling 3.0), `0afea44f…` (Kling 3.0 with end frame), `07a5cd03…` (Seedance with end frame)

Prompt used:

```
Photorealistic macro shot, overhead camera on a tripod, completely still for the first second while soft dappled forest light flickers through the leaves. Then the deep espresso wax seal stamped "I&H" cracks cleanly in two with a crisp snap and tiny wax flakes scatter on the paper. The translucent vellum band loosens and slides off both sides of the envelope. The deckled cream cotton flap slowly lifts open along its fold, revealing a deep espresso brown invitation card tucked inside. The card slides up out of the envelope and rises smoothly toward the camera until its blank deep espresso surface fills the entire frame. Natural physics, real paper weight, shallow depth of field. No hands, no people, no added text. Sound: quiet forest ambience with birdsong, a sharp wax crack, soft paper rustle, the card sliding out of the envelope.
```

How it's assembled (`tools/prep_apertura.sh`):
- `espera.mp4`: the first second played forward and backward, silent, as the idle loop before the tap.
- `apertura.mp4`: from 1.6 s (just before the crack) to the end, with its sound.
- `tarjeta.jpg`: the last frame (the card filling the frame), which becomes the background of the invitation.
- `musica.mp3`: the song from their save the date, fading in once the invitation opens.
