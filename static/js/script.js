// Weather App JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeWeatherApp();
});

function initializeWeatherApp() {
    // Auto-focus search input
    const searchInput = document.querySelector('input[name="city"]');
    if (searchInput) {
        searchInput.focus();
        
        // Add input suggestions
        setupSearchSuggestions(searchInput);
    }
    
    // Add smooth animations
    addSmoothAnimations();
    
    // Update time every minute
    updateCurrentTime();
    setInterval(updateCurrentTime, 60000);
    
    // Add refresh functionality
    setupRefresh();
}

function setupSearchSuggestions(input) {
    const popularCities = [
        'London', 'New York', 'Tokyo', 'Paris', 'Sydney',
        'Berlin', 'Moscow', 'Dubai', 'Singapore', 'Toronto',
        'Mumbai', 'Shanghai', 'Rome', 'Madrid', 'Seoul'
    ];
    
    input.addEventListener('focus', function() {
        // Could implement search suggestions here
        console.log('Input focused - suggestions could be implemented');
    });
}

function addSmoothAnimations() {
    // Add fade-in animation to weather cards
    const cards = document.querySelectorAll('.bg-white\\/20');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('animate-fade-in');
    });
}

function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });
    
    // Update any time displays if needed
    const timeElements = document.querySelectorAll('.current-time');
    timeElements.forEach(el => {
        el.textContent = timeString;
    });
}

function setupRefresh() {
    // Add pull-to-refresh or manual refresh
    let startY;
    
    document.addEventListener('touchstart', e => {
        startY = e.touches[0].clientY;
    });
    
    document.addEventListener('touchmove', e => {
        if (!startY) return;
        
        const currentY = e.touches[0].clientY;
        const diff = currentY - startY;
        
        if (diff > 100 && window.scrollY === 0) {
            // Pull to refresh
            location.reload();
        }
    });
}

// Weather utility functions
class WeatherUtils {
    static getWeatherIcon(condition) {
        const iconMap = {
            'clear': 'fas fa-sun',
            'clouds': 'fas fa-cloud',
            'rain': 'fas fa-cloud-rain',
            'snow': 'fas fa-snowflake',
            'thunderstorm': 'fas fa-bolt',
            'drizzle': 'fas fa-cloud-drizzle',
            'mist': 'fas fa-smog'
        };
        
        return iconMap[condition.toLowerCase()] || 'fas fa-cloud';
    }
    
    static formatTemperature(temp, unit = 'C') {
        return `${Math.round(temp)}°${unit}`;
    }
    
    static getWindDirection(degrees) {
        const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
        const index = Math.round(degrees / 22.5) % 16;
        return directions[index];
    }
}


// Add to existing script.js

// Favorite functionality
function setupFavoriteFunctionality() {
    const favoriteBtn = document.getElementById('favoriteBtn');
    if (favoriteBtn) {
        favoriteBtn.addEventListener('click', toggleFavorite);
    }
}

async function toggleFavorite() {
    const city = document.querySelector('input[name="city"]').value;
    const btn = document.getElementById('favoriteBtn');
    const isFavorite = btn.classList.contains('favorited');
    
    try {
        const response = await fetch('/favorite', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                city: city,
                action: isFavorite ? 'remove' : 'add'
            })
        });
        
        if (response.ok) {
            if (isFavorite) {
                btn.classList.remove('favorited');
                btn.innerHTML = '<i class="far fa-star mr-2"></i>Add to Favorites';
            } else {
                btn.classList.add('favorited');
                btn.innerHTML = '<i class="fas fa-star mr-2"></i>Remove from Favorites';
            }
        }
    } catch (error) {
        console.error('Error toggling favorite:', error);
    }
}

// Enhanced search with debouncing
function setupEnhancedSearch() {
    const searchInput = document.querySelector('input[name="city"]');
    let debounceTimer;
    
    searchInput.addEventListener('input', function(e) {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            if (e.target.value.length >= 3) {
                fetchSearchSuggestions(e.target.value);
            }
        }, 300);
    });
}

async function fetchSearchSuggestions(query) {
    // This would integrate with a city search API
    console.log('Fetching suggestions for:', query);
}

// Weather charts (using Chart.js - add CDN to base.html)
function setupWeatherCharts() {
    const ctx = document.getElementById('weatherChart');
    if (ctx) {
        // Initialize temperature chart for hourly forecast
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: weatherData.hourly.map(h => h.time),
                datasets: [{
                    label: 'Temperature °C',
                    data: weatherData.hourly.map(h => h.temp),
                    borderColor: 'rgb(255, 255, 255)',
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: 'white'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: 'white'
                        }
                    }
                }
            }
        });
    }
}

// Update initializeWeatherApp function
function initializeWeatherApp() {
    // Existing code...
    setupFavoriteFunctionality();
    setupEnhancedSearch();
    setupWeatherCharts();
}

// Geolocation support
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            showPosition,
            showError,
            { timeout: 10000 }
        );
    }
}

function showPosition(position) {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;
    
    // Reverse geocoding to get city name
    fetch(`/api/geolocation?lat=${lat}&lon=${lon}`)
        .then(response => response.json())
        .then(data => {
            if (data.city) {
                window.location.href = `/?city=${encodeURIComponent(data.city)}`;
            }
        });
}

function showError(error) {
    console.log('Geolocation error:', error);
}

// Add geolocation button to your HTML
function addGeolocationButton() {
    const header = document.querySelector('.max-w-md.mx-auto.px-4.py-4');
    if (header) {
        const geoButton = document.createElement('button');
        geoButton.innerHTML = '<i class="fas fa-location-arrow"></i>';
        geoButton.className = 'text-white ml-2 hover:text-white/80';
        geoButton.title = 'Use current location';
        geoButton.onclick = getLocation;
        
        const form = document.querySelector('#searchForm');
        form.appendChild(geoButton);
    }
}

// Export for global use
window.WeatherUtils = WeatherUtils;

