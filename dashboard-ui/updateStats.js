const STATS_API_URL = "http://runify-deployment.canadaeast.cloudapp.azure.com:8100/stats"
const EVENTS_URL = {
    running: "http://runify-deployment.canadaeast.cloudapp.azure.com:8110/running",
    music: "http://runify-deployment.canadaeast.cloudapp.azure.com:8110/music"
}
const ANOMALY_API_URL = "http://runify-deployment.canadaeast.cloudapp.azure.com:8120/anomalies"

let statsData = {
    num_running_stats: 0,
    num_music_info: 0
};

const getEvent = (eventType) => {
    const maxIndex = eventType === 'running' ? statsData.num_running_stats : statsData.num_music_info
    const eventIndex = Math.floor(Math.random() * maxIndex)

    fetch(`${EVENTS_URL[eventType]}?index=${eventIndex}`)
        .then(res => {
            if (!res.ok) {
                throw new Error(`Status code ${res.status}`)
            }
            return res.json()
        })
        .then((result) => {
            updateEventHTML(result, eventType)
        })
        .catch((error) => {
            updateEventHTML({ error: error.message }, eventType, true)
        })
}

const getStats = (statsUrl) => {
    fetch(statsUrl)
        .then(res => res.json())
        .then((result) => {
            statsData = result  
            updateStatsHTML(result)
            updateLastUpdated(result.last_updated)
        })
        .catch((error) => {
            updateStatsHTML({ error: error.message }, true)
        })
}

const updateStatsHTML = (data, error = false) => {
    const elem = document.getElementById("stats")
    if (error) {
        elem.innerHTML = `<code>${data.error}</code>`
        return
    }

    elem.innerHTML = ""
    const stats = [
        { label: "Total Runs", value: data.num_running_stats || 0 },
        { label: "Average Run Duration", value: `${data.avg_run_duration ? (data.avg_run_duration / 60).toFixed(2) : 'N/A'} minutes` },
        { label: "Max Run Distance", value: `${data.max_distance ? (data.max_distance / 1000).toFixed(2) : 'N/A'} km` },
        { label: "Total Songs", value: data.num_music_info || 0 },
        { label: "Average Song Duration", value: `${data.avg_song_duration ? (data.avg_song_duration / 60).toFixed(2) : 'N/A'} minutes` }
    ]

    stats.forEach(stat => {
        const p = document.createElement("p")
        p.innerHTML = `<strong>${stat.label}:</strong> ${stat.value}`
        elem.appendChild(p)
    })
}

const updateEventHTML = (data, eventType, error = false) => {
    const elem = document.getElementById(`event-${eventType}`)
    
    if (error) {
        elem.innerHTML = `<code>${data.error}</code>`
        return
    }

    elem.innerHTML = ""
    if (eventType === 'running') {
        elem.innerHTML = `
            <div class="event-details">
                <p><strong>User ID:</strong> ${data.user_id || 'N/A'}</p>
                <p><strong>Duration:</strong> ${data.duration ? (data.duration / 60).toFixed(2) : 'N/A'} minutes</p>
                <p><strong>Distance:</strong> ${data.distance ? (data.distance / 1000).toFixed(2) : 'N/A'} km</p>
                <p><strong>Time:</strong> ${data.timestamp ? new Date(data.timestamp).toLocaleString() : 'N/A'}</p>
                <p><strong>Trace ID:</strong> ${data.trace_id || 'N/A'}</p>
            </div>
        `
    } else if (eventType === 'music') {
        elem.innerHTML = `
            <div class="event-details">
                <p><strong>User ID:</strong> ${data.user_id || 'N/A'}</p>
                <p><strong>Song:</strong> ${data.song_name || 'N/A'}</p>
                <p><strong>Artist:</strong> ${data.artist || 'N/A'}</p>
                <p><strong>Duration:</strong> ${data.song_duration ? (data.song_duration / 60).toFixed(2) : 'N/A'} minutes</p>
                <p><strong>Time:</strong> ${data.timestamp ? new Date(data.timestamp).toLocaleString() : 'N/A'}</p>
                <p><strong>Trace ID:</strong> ${data.trace_id || 'N/A'}</p>
            </div>
        `
    }
}

const updateAnomalies = () => {
    fetch(ANOMALY_API_URL)
        .then(res => res.json())
        .then((anomalies) => {
            console.log('Received anomalies:', anomalies);  // Debug log

            if (anomalies.message) {
                console.log('No anomalies found');  // Debug log
                updateAnomalyHTML(null, 'running');
                updateAnomalyHTML(null, 'music');
                return;
            }

            const runningAnomalies = anomalies
                .filter(a => a.event_type === 'running_stats')
                .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
            
            const musicAnomalies = anomalies
                .filter(a => a.event_type === 'music_info')
                .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
            
            console.log('Filtered anomalies:', {  // Debug log
                running: runningAnomalies,
                music: musicAnomalies
            });

            updateAnomalyHTML(runningAnomalies[0], 'running');
            updateAnomalyHTML(musicAnomalies[0], 'music');
        })
        .catch((error) => {
            console.error('Error fetching anomalies:', error);  // Debug log
            updateAnomalyHTML({ error: error.message }, 'running', true);
            updateAnomalyHTML({ error: error.message }, 'music', true);
        });
}

const updateAnomalyHTML = (anomaly, type, error = false) => {
    const container = document.getElementById(`${type}-anomalies`);
    console.log(`Updating ${type} anomalies:`, { container, anomaly, error });  // Debug log
    
    if (!container) {
        console.error(`Container for ${type}-anomalies not found`);  // Debug log
        return;
    }

    if (error) {
        container.innerHTML = `<code>Error: ${anomaly.error}</code>`;
        return;
    }

    if (!anomaly) {
        container.innerHTML = '<p class="empty-anomaly">No anomalies detected</p>';
        return;
    }

    const timestamp = new Date(anomaly.timestamp);
    container.innerHTML = `
        <div class="anomaly-details">
            <p><strong>Type:</strong> ${anomaly.anomaly_type}</p>
            <p><strong>Event ID:</strong> ${anomaly.event_id}</p>
            <p><strong>Description:</strong> ${anomaly.description}</p>
            <p><strong>Detected:</strong> ${timestamp.toLocaleString()}</p>
            <p><strong>Trace ID:</strong> ${anomaly.trace_id}</p>
        </div>
    `;
    console.log(`Updated ${type} anomaly content`);  
}

const updateLastUpdated = (timestamp) => {
    const elem = document.getElementById("last-updated")
    const date = timestamp ? new Date(timestamp) : new Date()
    elem.textContent = `Last updated: ${date.toLocaleString()}`
}


const setup = () => {
    console.log('Dashboard setup starting');  // Debug log
    
    // Initial data load
    getStats(STATS_API_URL);
    getEvent("running");
    getEvent("music");
    updateAnomalies();  // Make sure this runs

    // Set up periodic updates
    setInterval(() => {
        getStats(STATS_API_URL);
        getEvent("running");
        getEvent("music");
        updateAnomalies();  // Make sure this runs in the interval
    }, 3000);

    console.log('Dashboard setup complete');  // Debug log
}

// Make sure this executes
console.log('Script loaded');
document.addEventListener('DOMContentLoaded', setup);