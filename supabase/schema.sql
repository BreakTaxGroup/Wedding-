-- Base de datos de la invitación (Supabase · proyecto boda-idanay-humberto · cuenta humbertovilliva@gmail.com)
-- Las tablas no se leen ni se escriben directamente: todo pasa por funciones.
--   Invitados (público): config_publica(), invitado_publico(codigo), mi_respuesta(codigo), responder(json)
--   Novios (requieren la clave): admin_ok, admin_datos, admin_guardar_invitados, admin_marcar_enviada,
--                                admin_borrar_invitado, admin_borrar_respuesta, admin_guardar_config
-- La clave de administración NO está aquí: en private.ajustes solo se guarda su huella sha256.
-- Para cambiarla:  update private.ajustes set clave_hash = encode(extensions.digest('NUEVA-CLAVE','sha256'),'hex');

create extension if not exists pgcrypto with schema extensions;
create schema if not exists private;
revoke all on schema private from public, anon, authenticated;

create table public.invitados(
  id text primary key check (id ~ '^[a-z0-9]{4,12}$'),
  tipo text not null default 'persona' check (tipo in ('persona','pareja','familia')),
  personas text[] not null default '{}',
  sobre text not null check (char_length(sobre) between 1 and 80),
  cupos int not null default 1 check (cupos between 1 and 20),
  idioma text not null default 'es' check (idioma in ('es','en')),
  nota text not null default '' check (char_length(nota) <= 300),
  telefono text not null default '' check (char_length(telefono) <= 40),
  enviada timestamptz,
  creado timestamptz not null default now(),
  actualizado timestamptz not null default now()
);
create table public.respuestas(
  id uuid primary key default gen_random_uuid(),
  codigo text unique check (codigo is null or codigo ~ '^[a-z0-9]{4,12}$'),
  nombre text not null check (char_length(nombre) between 1 and 120),
  asiste boolean not null,
  personas int not null default 0 check (personas between 0 and 20),
  asistentes text[] not null default '{}',
  acompanante text not null default '',
  alergias text not null default '',
  mensaje text not null default '',
  idioma text not null default 'es',
  fecha timestamptz not null default now()
);
create table public.config(id smallint primary key default 1 check (id = 1), data jsonb not null default '{}'::jsonb, actualizado timestamptz not null default now());
insert into public.config(id) values (1);
create table private.ajustes(id smallint primary key default 1 check (id = 1), clave_hash text not null);

alter table public.invitados enable row level security;
alter table public.respuestas enable row level security;
alter table public.config enable row level security;
revoke all on public.invitados, public.respuestas, public.config from anon, authenticated;

create or replace function private.es_admin(k text) returns boolean language sql stable security definer set search_path = '' as $$
  select exists(select 1 from private.ajustes a where a.clave_hash = encode(extensions.digest(coalesce(k,''), 'sha256'), 'hex')); $$;

create or replace function public.config_publica() returns jsonb language sql stable security definer set search_path = '' as $$ select data from public.config where id = 1 $$;
create or replace function public.invitado_publico(p_codigo text) returns jsonb language sql stable security definer set search_path = '' as $$
  select jsonb_build_object('tipo', i.tipo, 'personas', to_jsonb(i.personas), 'sobre', i.sobre, 'cupos', i.cupos, 'idioma', i.idioma, 'nota', i.nota)
  from public.invitados i where i.id = p_codigo and p_codigo ~ '^[a-z0-9]{4,12}$' $$;
create or replace function public.mi_respuesta(p_codigo text) returns jsonb language sql stable security definer set search_path = '' as $$
  select to_jsonb(r) - 'id' from public.respuestas r where r.codigo = p_codigo and p_codigo ~ '^[a-z0-9]{4,12}$' $$;

create or replace function public.responder(p jsonb) returns jsonb language plpgsql security definer set search_path = '' as $$
declare v_codigo text := nullif(trim(coalesce(p->>'codigo','')), ''); v jsonb;
begin
  if v_codigo is not null and v_codigo !~ '^[a-z0-9]{4,12}$' then raise exception 'codigo invalido'; end if;
  if coalesce(trim(p->>'nombre'),'') = '' then raise exception 'falta nombre'; end if;
  insert into public.respuestas as r(codigo,nombre,asiste,personas,asistentes,acompanante,alergias,mensaje,idioma,fecha)
  values(v_codigo, left(trim(p->>'nombre'),120), coalesce((p->>'asiste')::boolean,false), least(greatest(coalesce((p->>'personas')::int,0),0),20),
         coalesce(array(select left(x,120) from jsonb_array_elements_text(coalesce(p->'asistentes','[]'::jsonb)) x limit 20),'{}'),
         left(coalesce(p->>'acompanante',''),80), left(coalesce(p->>'alergias',''),300), left(coalesce(p->>'mensaje',''),1200),
         case when p->>'idioma' = 'en' then 'en' else 'es' end, now())
  on conflict (codigo) do update set nombre=excluded.nombre, asiste=excluded.asiste, personas=excluded.personas, asistentes=excluded.asistentes,
     acompanante=excluded.acompanante, alergias=excluded.alergias, mensaje=excluded.mensaje, idioma=excluded.idioma, fecha=now()
  returning to_jsonb(r) - 'id' into v;
  return v;
end $$;

create or replace function public.admin_ok(k text) returns boolean language sql stable security definer set search_path = '' as $$ select private.es_admin(k) $$;
create or replace function public.admin_datos(k text) returns jsonb language plpgsql stable security definer set search_path = '' as $$
begin
  if not private.es_admin(k) then raise exception 'no autorizado' using errcode = '42501'; end if;
  return jsonb_build_object(
    'invitados', coalesce((select jsonb_agg(to_jsonb(i) order by i.creado) from public.invitados i), '[]'::jsonb),
    'respuestas', coalesce((select jsonb_agg(to_jsonb(r) order by r.fecha) from public.respuestas r), '[]'::jsonb),
    'config', (select data from public.config where id = 1));
end $$;
create or replace function public.admin_guardar_invitados(k text, items jsonb) returns int language plpgsql security definer set search_path = '' as $$
declare it jsonb; n int := 0;
begin
  if not private.es_admin(k) then raise exception 'no autorizado' using errcode = '42501'; end if;
  for it in select * from jsonb_array_elements(items) loop
    insert into public.invitados as i(id,tipo,personas,sobre,cupos,idioma,nota,telefono,enviada,creado,actualizado)
    values(it->>'id', coalesce(it->>'tipo','persona'),
           coalesce(array(select left(x,120) from jsonb_array_elements_text(coalesce(it->'personas','[]'::jsonb)) x limit 20),'{}'),
           left(trim(it->>'sobre'),80), coalesce((it->>'cupos')::int,1), coalesce(it->>'idioma','es'), left(coalesce(it->>'nota',''),300),
           left(coalesce(it->>'telefono',''),40), nullif(it->>'enviada','')::timestamptz, coalesce(nullif(it->>'creado','')::timestamptz, now()), now())
    on conflict (id) do update set tipo=excluded.tipo, personas=excluded.personas, sobre=excluded.sobre, cupos=excluded.cupos, idioma=excluded.idioma,
       nota=excluded.nota, telefono=excluded.telefono, enviada=excluded.enviada, actualizado=now();
    n := n + 1;
  end loop;
  return n;
end $$;
create or replace function public.admin_marcar_enviada(k text, p_id text, p_enviada timestamptz) returns void language plpgsql security definer set search_path = '' as $$
begin if not private.es_admin(k) then raise exception 'no autorizado' using errcode = '42501'; end if;
  update public.invitados set enviada = p_enviada, actualizado = now() where id = p_id; end $$;
create or replace function public.admin_borrar_invitado(k text, p_id text) returns void language plpgsql security definer set search_path = '' as $$
begin if not private.es_admin(k) then raise exception 'no autorizado' using errcode = '42501'; end if;
  delete from public.invitados where id = p_id; end $$;
create or replace function public.admin_borrar_respuesta(k text, p_id uuid) returns void language plpgsql security definer set search_path = '' as $$
begin if not private.es_admin(k) then raise exception 'no autorizado' using errcode = '42501'; end if;
  delete from public.respuestas where id = p_id; end $$;
create or replace function public.admin_guardar_config(k text, p_data jsonb) returns void language plpgsql security definer set search_path = '' as $$
begin if not private.es_admin(k) then raise exception 'no autorizado' using errcode = '42501'; end if;
  update public.config set data = coalesce(p_data,'{}'::jsonb), actualizado = now() where id = 1; end $$;

revoke execute on all functions in schema private from public, anon, authenticated;
grant execute on function public.config_publica(), public.invitado_publico(text), public.mi_respuesta(text), public.responder(jsonb),
  public.admin_ok(text), public.admin_datos(text), public.admin_guardar_invitados(text,jsonb), public.admin_marcar_enviada(text,text,timestamptz),
  public.admin_borrar_invitado(text,text), public.admin_borrar_respuesta(text,uuid), public.admin_guardar_config(text,jsonb) to anon, authenticated;
