<script setup>
import { onMounted, ref, computed } from "vue";

const KAKAO_KEY = import.meta.env.VITE_KAKAO_MAP_KEY;

const mapEl = ref(null);
const map = ref(null);
const placesService = ref(null);

const regionData = ref([]);   // data.json mapInfo
const bankList = ref([]);     // data.json bankInfo

const selectedSido = ref("");
const selectedGugun = ref("");
const selectedBank = ref("");

const gugunOptions = computed(() => {
  const region = regionData.value.find(r => r.name === selectedSido.value);
  return region ? region.countries : [];
});

const isSearchEnabled = computed(() => {
  return !!(selectedSido.value && selectedGugun.value && selectedBank.value);
});

let markers = [];
let infoWindows = [];

function resetSelectionsOnSidoChange() {
  selectedGugun.value = "";
}

function clearMarkers() {
  markers.forEach(m => m.setMap(null));
  markers = [];
  infoWindows.forEach(iw => iw.close());
  infoWindows = [];
}

function initMap() {
  const gangnamStation = new window.kakao.maps.LatLng(37.49818, 127.027386);

  map.value = new window.kakao.maps.Map(mapEl.value, {
    center: gangnamStation,
    level: 3,
  });

  new window.kakao.maps.Marker({
    position: gangnamStation,
    map: map.value,
  });

  placesService.value = new window.kakao.maps.services.Places(map.value);
}

async function loadData() {
  // public/data.json -> /data.json 으로 접근 가능
  const res = await fetch("/data.json");
  const data = await res.json();
  regionData.value = data.mapInfo || [];
  bankList.value = data.bankInfo || [];
}

function placesSearchCB(data, status) {
  const kakao = window.kakao;

  if (status === kakao.maps.services.Status.OK) {
    const bounds = new kakao.maps.LatLngBounds();

    data.forEach((place) => {
      const position = new kakao.maps.LatLng(place.y, place.x);

      const marker = new kakao.maps.Marker({
        map: map.value,
        position,
      });
      markers.push(marker);
      bounds.extend(position);

      const addr = place.road_address_name || place.address_name || "";
      const iwContent = `
        <div style="padding:6px;font-size:12px;line-height:1.35;">
          <strong>${place.place_name}</strong><br/>
          ${addr}
        </div>
      `;
      const infowindow = new kakao.maps.InfoWindow({ content: iwContent });
      infoWindows.push(infowindow);

      kakao.maps.event.addListener(marker, "click", () => {
        infoWindows.forEach(iw => iw.close());
        infowindow.open(map.value, marker);
      });
    });

    map.value.setBounds(bounds);
  } else if (status === window.kakao.maps.services.Status.ZERO_RESULT) {
    alert("검색 결과가 없습니다.");
  } else {
    alert("검색 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.");
  }
}

function onSearch() {
  if (!isSearchEnabled.value) return;

  const keyword = `${selectedSido.value} ${selectedGugun.value} ${selectedBank.value}`;

  clearMarkers();
  placesService.value.keywordSearch(keyword, placesSearchCB);
}

function loadKakaoScript() {
  return new Promise((resolve, reject) => {
    if (!KAKAO_KEY) {
      reject(new Error("VITE_KAKAO_MAP_KEY가 설정되지 않았습니다 (.env 확인)"));
      return;
    }

    // 이미 로드되어 있으면 재삽입 안 함
    if (window.kakao && window.kakao.maps) {
      resolve();
      return;
    }

    const script = document.createElement("script");
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${KAKAO_KEY}&autoload=false&libraries=services`;
    script.async = true;

    script.onload = () => resolve();
    script.onerror = () => reject(new Error("카카오맵 SDK 로드 실패"));

    document.head.appendChild(script);
  });
}

onMounted(async () => {
  try {
    await loadKakaoScript();

    window.kakao.maps.load(async () => {
      initMap();
      await loadData();
    });
  } catch (e) {
    console.error(e);
    alert(e.message || "지도 초기화 실패");
  }
});
</script>

<template>
  <div class="page">
    <header class="header">💳 내 주변 은행 찾기 💳</header>

    <div class="container">
      <aside class="panel">
        <h2>은행 찾기</h2>

        <div class="form-group">
          <label>광역시 / 도</label>
          <select v-model="selectedSido" @change="resetSelectionsOnSidoChange">
            <option value="">광역시 / 도를 선택하세요</option>
            <option v-for="r in regionData" :key="r.name" :value="r.name">
              {{ r.name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>시 / 군 / 구</label>
          <select v-model="selectedGugun" :disabled="!selectedSido">
            <option value="">시 / 군 / 구를 선택하세요</option>
            <option v-for="g in gugunOptions" :key="g" :value="g">
              {{ g }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>은행</label>
          <select v-model="selectedBank" :disabled="bankList.length === 0">
            <option value="">은행을 선택하세요</option>
            <option v-for="b in bankList" :key="b" :value="b">
              {{ b }}
            </option>
          </select>
        </div>

        <button class="btn" :disabled="!isSearchEnabled" @click="onSearch">
          검색
        </button>

        <p class="hint">
          * 선택 후 검색하면 해당 지역의 은행 지점을 표시합니다.
        </p>
      </aside>

      <div class="map" ref="mapEl"></div>
    </div>
  </div>
</template>

<style scoped>
.page { height: calc(100vh - 60px); }
.header {
  background: #f36c21;
  color: #fff;
  padding: 10px 20px;
  font-weight: 800;
}
.container {
  display: flex;
  height: calc(100vh - 110px);
}
.panel {
  width: 280px;
  background: #fff7f0;
  border-right: 1px solid #e0e0e0;
  padding: 15px;
}
.panel h2 {
  margin: 0 0 12px;
  padding: 8px 10px;
  font-size: 16px;
  background: #f36c21;
  color: #fff;
  border-radius: 6px;
}
.form-group { margin-bottom: 12px; }
label { display: block; font-size: 13px; margin-bottom: 6px; }
select {
  width: 100%;
  padding: 6px;
  border: 1px solid #ccc;
  border-radius: 6px;
}
.btn {
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 8px;
  background: #f36c21;
  color: #fff;
  font-weight: 800;
  cursor: pointer;
}
.btn:disabled { background: #ccc; cursor: not-allowed; }
.hint { margin-top: 10px; font-size: 12px; color: #555; }
.map { flex: 1; min-width: 0; }
</style>
