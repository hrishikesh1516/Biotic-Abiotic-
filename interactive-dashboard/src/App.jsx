import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import axios from 'axios';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, 
  ResponsiveContainer, Legend 
} from 'recharts';
import { Activity, Droplets, Thermometer, FlaskConical, Beaker, Sprout, Loader2 } from 'lucide-react';

// Fix leaflet icon issue in React
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

function MapUpdater({ center }) {
  const map = useMap();
  useEffect(() => {
    if (center) map.flyTo(center, 6, { animate: true, duration: 1.5 });
  }, [center, map]);
  return null;
}

function LocationSelector({ setLocation, fetchPointData }) {
  useMapEvents({
    click(e) {
      setLocation(e.latlng);
      fetchPointData(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

const StatCard = ({ icon: Icon, label, value, unit, color }) => (
  <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50 flex items-center space-x-4 hover:bg-slate-700/50 transition-colors">
    <div className={`p-3 rounded-lg bg-${color}-500/20 text-${color}-400`}>
      <Icon size={24} />
    </div>
    <div>
      <p className="text-sm text-slate-400 font-medium">{label}</p>
      <div className="flex items-baseline space-x-1">
        <span className="text-xl font-bold text-white">{value !== null && value !== undefined ? value.toFixed(3) : 'N/A'}</span>
        <span className="text-xs text-slate-500">{unit}</span>
      </div>
    </div>
  </div>
);

function App() {
  const [location, setLocation] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('physics'); // physics, bgc, npp
  const [inputLat, setInputLat] = useState('');
  const [inputLon, setInputLon] = useState('');

  const fetchPointData = async (lat, lon) => {
    setLoading(true);
    setError(null);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080';
      const response = await axios.get(`${apiUrl}/api/data`, {
        params: { lat, lon }
      });
      setData(response.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to fetch data for this location. Make sure the Python backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleManualSearch = () => {
    const lat = parseFloat(inputLat);
    const lon = parseFloat(inputLon);
    if (!isNaN(lat) && !isNaN(lon)) {
      setLocation({ lat, lng: lon });
      fetchPointData(lat, lon);
    }
  };

  return (
    <div className="flex w-screen h-screen overflow-hidden bg-slate-900 text-slate-100">
      {/* Map Container */}
      <div className="flex-1 relative h-full">
        <MapContainer 
          center={[15.0, 75.0]} 
          zoom={5} 
          className="absolute inset-0 w-full h-full"
          maxBounds={[[0, 50], [35, 100]]}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />
          <LocationSelector setLocation={setLocation} fetchPointData={fetchPointData} />
          <MapUpdater center={location} />
          {location && <Marker position={location} />}
        </MapContainer>

        {/* Floating Manual Coordinate Search */}
        <div className="absolute top-6 left-1/2 transform -translate-x-1/2 z-[1000] glass px-4 py-3 rounded-2xl shadow-2xl flex items-center space-x-3 border border-slate-600/50">
          <div className="flex flex-col">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider mb-1 ml-1 font-semibold">Latitude</span>
            <input 
              type="number" 
              placeholder="e.g. 15.5" 
              className="bg-slate-900/60 text-white px-3 py-2 rounded-lg border border-slate-600 focus:outline-none focus:border-teal-400 w-28 text-sm"
              value={inputLat}
              onChange={(e) => setInputLat(e.target.value)}
            />
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider mb-1 ml-1 font-semibold">Longitude</span>
            <input 
              type="number" 
              placeholder="e.g. 75.2" 
              className="bg-slate-900/60 text-white px-3 py-2 rounded-lg border border-slate-600 focus:outline-none focus:border-teal-400 w-28 text-sm"
              value={inputLon}
              onChange={(e) => setInputLon(e.target.value)}
            />
          </div>
          <button 
            onClick={handleManualSearch}
            className="mt-5 bg-teal-600 hover:bg-teal-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center shadow-lg shadow-teal-900/50"
          >
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
            Search
          </button>
        </div>

        {/* Helper prompt when empty */}
        {!location && (
          <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 glass px-6 py-3 rounded-full shadow-2xl animate-bounce z-[1000] pointer-events-none">
            <p className="text-teal-400 font-medium tracking-wide">📍 Click anywhere on the map to extract data</p>
          </div>
        )}
      </div>

      {/* Dashboard Side Panel */}
      <div 
        className={`h-full bg-slate-900 border-l border-slate-700/50 shadow-2xl transition-all duration-300 ease-in-out overflow-hidden flex-shrink-0 ${
          location ? 'w-[500px]' : 'w-0 border-none'
        }`}
      >
        <div className="w-[500px] h-full flex flex-col overflow-y-auto">
          
          {/* Header */}
          <div className="p-6 border-b border-slate-700/50 bg-slate-900/40 flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-teal-400">
                Paleobiology Explorer
              </h1>
              <p className="text-slate-400 text-sm mt-1">15-Year Average (5-50m Depth)</p>
            </div>
            {/* Close Button */}
            <button 
              onClick={() => setLocation(null)}
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
              title="Close Dashboard"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          {location && (
            <div className="px-6 pt-4 pb-2">
              <div className="flex items-center space-x-2 text-sm text-teal-300 bg-teal-900/30 px-3 py-2 rounded-lg border border-teal-800/50">
                <span className="font-semibold">Selected Location:</span>
                <span>{location.lat.toFixed(4)}° N, {location.lng.toFixed(4)}° E</span>
              </div>
            </div>
          )}

          {/* Content */}
          <div className="p-6 flex-1 flex flex-col space-y-6">
            {loading ? (
              <div className="flex flex-col items-center justify-center h-64 space-y-4">
                <Loader2 className="w-10 h-10 text-teal-500 animate-spin" />
                <p className="text-slate-400 animate-pulse">Slicing decades of data...</p>
              </div>
            ) : error ? (
              <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-lg text-sm">
                {error}
              </div>
            ) : data ? (
              <>
                {/* Stats Grid */}
                <div className="grid grid-cols-2 gap-4">
                  <StatCard icon={Thermometer} label="Sea Temp" value={data.averages.sst} unit="°C" color="orange" />
                  <StatCard icon={Droplets} label="Salinity" value={data.averages.salinity} unit="PSU" color="blue" />
                  <StatCard icon={Sprout} label="NPP" value={data.averages.npp} unit="mg C/m²/d" color="emerald" />
                  <StatCard icon={Activity} label="pH" value={data.averages.ph} unit="" color="purple" />
                  <StatCard icon={FlaskConical} label="Nitrates" value={data.averages.nitrate} unit="mmol/m³" color="pink" />
                  <StatCard icon={Beaker} label="Phosphates" value={data.averages.phosphate} unit="mmol/m³" color="cyan" />
                </div>

                {/* Chart Tabs */}
                <div className="bg-slate-800/40 rounded-xl border border-slate-700/50 overflow-hidden flex-1 flex flex-col min-h-[350px]">
                  <div className="flex border-b border-slate-700/50 bg-slate-900/50">
                    {['physics', 'bgc', 'npp'].map((tab) => (
                      <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`flex-1 py-3 text-sm font-medium transition-colors uppercase tracking-wider ${
                          activeTab === tab 
                            ? 'text-teal-400 border-b-2 border-teal-400 bg-slate-800/50' 
                            : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/30'
                        }`}
                      >
                        {tab}
                      </button>
                    ))}
                  </div>
                  
                  <div className="p-4 flex-1">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={data.timeseries}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                        <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} tickMargin={10} minTickGap={30} />
                        <YAxis stroke="#94a3b8" fontSize={12} width={45} />
                        <RechartsTooltip 
                          contentStyle={{ backgroundColor: '#1e293b', borderColor: '#475569', color: '#f8fafc', borderRadius: '0.5rem' }}
                          itemStyle={{ color: '#e2e8f0', fontSize: '14px' }}
                          labelStyle={{ color: '#94a3b8', marginBottom: '4px' }}
                        />
                        <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                        
                        {activeTab === 'physics' && (
                          <>
                            <Line type="monotone" dataKey="sst" name="Temp (°C)" stroke="#f97316" strokeWidth={2} dot={false} activeDot={{ r: 6 }} />
                            <Line type="monotone" dataKey="salinity" name="Salinity" stroke="#3b82f6" strokeWidth={2} dot={false} />
                          </>
                        )}
                        
                        {activeTab === 'bgc' && (
                          <>
                            <Line type="monotone" dataKey="ph" name="pH" stroke="#a855f7" strokeWidth={2} dot={false} />
                            <Line type="monotone" dataKey="nitrate" name="Nitrate" stroke="#ec4899" strokeWidth={2} dot={false} />
                            <Line type="monotone" dataKey="phosphate" name="Phosphate" stroke="#06b6d4" strokeWidth={2} dot={false} />
                          </>
                        )}
                        
                        {activeTab === 'npp' && (
                          <Line type="monotone" dataKey="npp" name="NPP" stroke="#10b981" strokeWidth={2} dot={false} activeDot={{ r: 6 }} />
                        )}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
