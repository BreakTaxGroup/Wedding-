// Visita diaria (cron de Vercel) para que la base de datos gratuita de Supabase no se pause por inactividad.
module.exports = async (req, res) => {
  try {
    const r = await fetch('https://jvfopaaktgftvwnftcde.supabase.co/rest/v1/rpc/config_publica', {
      method: 'POST',
      headers: { apikey: 'sb_publishable_q4XVge1Ds5Ej4UZux80WCQ_D1q7IJNx', 'Content-Type': 'application/json' },
      body: '{}'
    });
    res.status(r.ok ? 200 : 502).json({ ok: r.ok, status: r.status, at: new Date().toISOString() });
  } catch (e) {
    res.status(502).json({ ok: false, error: String(e), at: new Date().toISOString() });
  }
};
