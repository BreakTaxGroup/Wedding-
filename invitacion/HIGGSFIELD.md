# Higgsfield: the hyperrealistic envelope

The connector in this session can read your Higgsfield account but can't generate. So you generate the two pieces at higgsfield.ai, and Claude downloads them from your history (`show_generations`) and swaps them into the invitation. Nothing needs to be uploaded or sent by hand.

## 1. The envelope image (generate this first)

- **Model:** Nano Banana Pro (or GPT Image 2 in high quality)
- **Format:** 9:16 vertical · 2K
- **Reference image:** the photo of the handmade-paper envelope with the wax seal (the one with "V&A")

```
Hyperrealistic overhead photograph of a single handmade cotton-paper wedding envelope with soft torn deckled edges, warm ivory color, lying on a moss-covered log in a lush forest. A narrow translucent vellum band wraps the left side of the envelope, with a pressed fern sprig, olive leaves and tiny dark burgundy berries visible beneath it. The pointed deckled flap is closed and sealed at the center with a glossy deep espresso brown wax seal (dark chocolate brown, #3A2218), irregular poured edges, embossed with the monogram "I&H" in classic Roman capitals inside a thin raised ring. No writing anywhere on the envelope, no names, no labels. Dappled late-afternoon sunlight through the forest canopy, soft leaf shadows on the paper, ferns around the edges, shallow depth of field, 100mm macro lens, ultra-detailed paper fibers and wax texture, photorealistic. Vertical composition, envelope centered and filling about 80% of the width, wax seal slightly above the center of the frame.
```

## 2. The seal breaking (video, using image 1 as the first frame)

- **Model:** Seedance 2.0 (or Cinema Studio Video 3.0)
- **Start image:** the envelope from step 1 · **Format:** 9:16 · 5 seconds · 1080p · **audio on**

```
Locked-off static camera on a tripod: absolutely no camera movement, no zoom, no pan for the whole shot. The deep espresso wax seal cracks sharply into two pieces along a jagged line through the "I&H" monogram, with a crisp snap; the two wax halves lift slightly and separate a few millimeters; a few tiny wax crumbs fall onto the paper; a soft warm golden light glows from inside the crack. Everything else stays exactly as in the first frame: the envelope, the vellum band, the pressed plants, the log and the light. Only gentle leaf shadows move with a light breeze. Photorealistic, no hands, no people, no text, no new objects.
```

The camera must stay still: the push toward the seal and the moment the invitation opens out of the seal are done by the page, and the guest's name is written on top of the envelope.

## When it's ready

Tell Claude "ready" in the chat. It looks up the latest image and video in your history, downloads them, and:
1. marks where the seal and the space for the name are,
2. syncs the crack with the opening of the portal,
3. republishes the invitation at the same link.

With 110 credits, it's enough for the image (a few credits) and one or two video attempts. Higgsfield shows the cost before you generate.
