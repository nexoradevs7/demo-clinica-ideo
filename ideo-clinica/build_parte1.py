# -*- coding: utf-8 -*-
"""Genera index.html de Clínica IDEO por bloques para evitar truncamiento."""

PARTES = []

PARTES.append("""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0F172A">
<title>Clínica IDEO · Líderes en Salud Visual y Cirugía Oftalmológica en Maracaibo</title>
<meta name="description" content="IDEO, Instituto Docente de Especialidades Oftalmológicas en Maracaibo. 20 años cuidando tu salud visual: oftalmología general, retina y vítreo, cirugía refractiva, oftalmopediatría y cirugía plástica ocular.">
<meta property="og:type" content="website">
<meta property="og:title" content="Clínica IDEO · Salud Visual en Maracaibo">
<meta property="og:description" content="20 años de trayectoria. Agende su cita con los especialistas oftalmológicos de Maracaibo.">
<meta property="og:locale" content="es_VE">
<link rel="canonical" href="https://www.ideo.com.ve/">

<link rel="preconnect" href="https://cdn.tailwindcss.com">
<link rel="preconnect" href="https://cdnjs.cloudflare.com" crossorigin>
<link rel="preconnect" href="https://images.unsplash.com">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="dns-prefetch" href="https://wa.me">

<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%230F172A'/%3E%3Cellipse cx='32' cy='32' rx='20' ry='12' fill='none' stroke='%2338BDF8' stroke-width='4'/%3E%3Ccircle cx='32' cy='32' r='6' fill='%2338BDF8'/%3E%3C/svg%3E">

<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = {
  theme: {
    extend: {
      colors: {
        ink: { DEFAULT: '#0F172A', 800: '#1E3A8A' },
        sky: { 50: '#F0F9FF', 400: '#38BDF8', 500: '#0284C7' },
        paper: { DEFAULT: '#F8FAFC', 200: '#E2E8F0' }
      },
      fontFamily: { sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'] },
      boxShadow: {
        soft: '0 10px 30px -12px rgba(15,23,42,.18)',
        lift: '0 18px 45px -18px rgba(15,23,42,.35)'
      }
    }
  }
};
</script>

<style>
  html { scroll-behavior: smooth; -webkit-text-size-adjust: 100%; }
  body { -webkit-font-smoothing: antialiased; }
  .media { position: relative; overflow: hidden; background: #E2E8F0; }
  .img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0; transition: opacity .45s ease; }
  .img.is-loaded { opacity: 1; }
  .skeleton:not(.done)::after { content: ""; position: absolute; inset: 0; z-index: 1;
    background: linear-gradient(100deg, #E2E8F0 20%, #F1F5F9 40%, #E2E8F0 60%);
    background-size: 220% 100%; animation: shimmer 1.4s linear infinite; }
  @keyframes shimmer { to { background-position: -220% 0; } }
  .reveal { opacity: 0; transform: translateY(18px); transition: opacity .6s ease, transform .6s cubic-bezier(.2,.7,.2,1); }
  .reveal.in { opacity: 1; transform: none; }
  .glass { background: rgba(15,23,42,.86); backdrop-filter: saturate(140%) blur(10px); }
  @supports not (backdrop-filter: blur(1px)) { .glass { background: #0F172A; } }
  .fa-icono { display: inline-flex; align-items: center; justify-content: center; width: 1.25em; height: 1em; }
  ::selection { background: #38BDF8; color: #0F172A; }
  [id] { scroll-margin-top: 84px; }
  @media (prefers-reduced-motion: reduce) {
    html { scroll-behavior: auto; }
    *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; }
    .reveal { opacity: 1; transform: none; }
  }
</style>

<!-- Font Awesome + Inter: carga asincrona, no bloquean el render -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css"
      media="print" onload="this.media='all'" crossorigin="anonymous" referrerpolicy="no-referrer">
<noscript><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css"></noscript>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
      media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap"></noscript>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "MedicalClinic",
  "name": "Clinica IDEO",
  "alternateName": "Instituto Docente de Especialidades Oftalmologicas",
  "url": "https://www.ideo.com.ve/",
  "telephone": "+58 424-6802187",
  "priceRange": "$$",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Calle 69A con Av. 17 - Baralt, Edificio IDEO",
    "addressLocality": "Maracaibo",
    "addressRegion": "Zulia",
    "addressCountry": "VE"
  },
  "medicalSpecialty": "Ophthalmologic",
  "openingHoursSpecification": [
    { "@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"], "opens": "08:00", "closes": "18:00" },
    { "@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "08:00", "closes": "13:00" }
  ]
}
</script>
</head>

<body class="bg-paper font-sans text-slate-700 antialiased">

<a href="#servicios" class="sr-only focus:not-sr-only focus:fixed focus:left-3 focus:top-3 focus:z-[100] focus:rounded-lg focus:bg-sky-400 focus:px-4 focus:py-2 focus:font-semibold focus:text-ink">Saltar al contenido</a>
""")

PARTES.append(open('parte_header.html', encoding='utf-8').read() if False else "")
