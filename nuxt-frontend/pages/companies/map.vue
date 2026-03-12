<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-gray-900">Company Locations</h1>
      <NuxtLink to="/companies" class="btn-primary">Browse Companies</NuxtLink>
    </div>
    <div id="map" class="w-full rounded-lg shadow-lg" style="height: 600px"></div>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig();
const api = useApi();

// server: false keeps this client-only so the #map div is mounted before initMap runs
const { data: companies } = await useAsyncData("map-companies", () => api.get<Company[]>("/companies/"), { server: false });

let mapInitialized = false;

onMounted(async () => {
  if (!companies.value?.length) return;
  await loadGoogleMapsScript(config.public.googleMapsApiKey as string);
  mapInitialized = true;
  initMap();
});

// Safety net: if companies loads after onMounted (network lag), init then
watch(companies, async (val) => {
  if (!mapInitialized && val?.length) {
    await loadGoogleMapsScript(config.public.googleMapsApiKey as string);
    mapInitialized = true;
    initMap();
  }
});

function loadGoogleMapsScript(apiKey: string): Promise<void> {
  return new Promise((resolve) => {
    if (typeof google !== "undefined" && google.maps) {
      resolve();
      return;
    }
    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}`;
    script.onload = () => resolve();
    document.head.appendChild(script);
  });
}

async function initMap() {
  const geoCompanies = (companies.value ?? []).filter((c: Company) => c.latitude && c.longitude);
  if (!geoCompanies.length) return;

  let styleData: google.maps.MapTypeStyle[] = [];
  try {
    const r = await fetch("http://127.0.0.1:8000/static/style.json");
    if (r.ok) styleData = (await r.json()) as google.maps.MapTypeStyle[];
  } catch {
    /* ignore */
  }

  const first = geoCompanies[0]!;
  const center: google.maps.LatLngLiteral = {
    lat: parseFloat(first.latitude),
    lng: parseFloat(first.longitude),
  };

  const mapEl = document.getElementById("map");
  if (!mapEl) return;

  const map = new google.maps.Map(mapEl, {
    zoom: geoCompanies.length === 1 ? 12 : 6,
    center,
    streetViewControl: false,
    fullscreenControl: true,
    styles: styleData,
  });

  geoCompanies.forEach((company: Company) => {
    const marker = new google.maps.Marker({
      position: { lat: parseFloat(company.latitude), lng: parseFloat(company.longitude) },
      map,
      title: company.name,
      animation: google.maps.Animation.DROP,
    });

    const infoWindow = new google.maps.InfoWindow({
      content: `
        <div style="max-width:280px;padding:10px">
          <h3 style="margin:0 0 6px;font-size:16px;font-weight:bold">${company.name}</h3>
          <p style="margin:0 0 4px;color:#6b7280;font-size:13px">${company.field}</p>
          <p style="margin:0 0 8px;color:#6b7280;font-size:12px">${company.address}</p>
          <a href="/companies/${company.id}" style="color:#4f46e5;font-weight:500;font-size:13px">View details →</a>
        </div>
      `,
      maxWidth: 320,
    });

    marker.addListener("click", () => infoWindow.open(map, marker));
  });

  if (geoCompanies.length > 1) {
    const bounds = new google.maps.LatLngBounds();
    geoCompanies.forEach((c: Company) => bounds.extend({ lat: parseFloat(c.latitude), lng: parseFloat(c.longitude) }));
    map.fitBounds(bounds);
  }
}
</script>
