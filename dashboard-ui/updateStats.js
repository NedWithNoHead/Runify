const STATS_API_URL = "http://runify-deployment.canadaeast.cloudapp.azure.com:8100/stats"
const EVENTS_URL = {
    running: "http://runify-deployment.canadaeast.cloudapp.azure.com:8110/running",
    music: "http://runify-deployment.canadaeast.cloudapp.azure.com:8110/music"
}

const getStats = (statsUrl) => {
    fetch(statsUrl)
        .then(res => res.json())
        .then((result) => {
            console.log("Received stats", result)
            updateStatsHTML(result)
            updateLastUpdated(result.last_updated)
        })
        .catch((error) => {
            updateStatsHTML({ error: error.message }, true)
        })
}

const getEvent = (eventType) => {
    const eventIndex = Math.floor(Math.random() * 100)

    fetch(`${EVENTS_URL[eventType]}?index=${eventIndex}`)
        .then(res => {
            if (!res.ok) {
                throw new Error(`Status code ${res.status}`)
            }
            return res.json()
        })
        .then((result) => {
            console.log(`Received ${eventType} event`, result)
            updateEventHTML(result, eventType)
        })
        .catch((error) => {
            updateEventHTML({ error: error.message }, eventType, true)
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
        { label: "Total Runs", value: data.num_running_stats },
        { label: "Average Run Duration", value: `${(data.avg_run_duration / 60).toFixed(2)} minutes` },
        { label: "Max Run Distance", value: `${(data.max_run_distance / 1000).toFixed(2)} km` },
        { label: "Total Songs", value: data.num_music_info },
        { label: "Average Song Duration", value: `${(data.avg_song_duration / 60).toFixed(2)} minutes` }
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

    let html = ''
    if (eventType === 'running') {
        html = `
            <p><strong>User ID:</strong> ${data.user_id}</p>
            <p><strong>Duration:</strong> ${(data.duration / 60).toFixed(2)} minutes</p>
            <p><strong>Distance:</strong> ${(data.distance / 1000).toFixed(2)} km</p>
            <p><strong>Time:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
        `
    } else {
        html = `
            <p><strong>User ID:</strong> ${data.user_id}</p>
            <p><strong>Song:</strong> ${data.song_name}</p>
            <p><strong>Artist:</strong> ${data.artist}</p>
            <p><strong>Duration:</strong> ${(data.song_duration / 60).toFixed(2)} minutes</p>
            <p><strong>Time:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
        `
    }
    elem.innerHTML = html
}

const updateLastUpdated = (timestamp) => {
    const elem = document.getElementById("last-updated")
    const date = timestamp ? new Date(timestamp) : new Date()
    elem.textContent = `Last updated: ${date.toLocaleString()}`
}

const setup = () => {
    getStats(STATS_API_URL)
    getEvent("running")
    getEvent("music")

    setInterval(() => {
        getStats(STATS_API_URL)
        getEvent("running")
        getEvent("music")
    }, 3000)
}

document.addEventListener('DOMContentLoaded', setup)