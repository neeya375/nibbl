(() => {
const restaurants = window.restaurants;
const restaurantContainer = document.getElementById("restaurantContainer");
const featuredContainer = document.getElementById("featuredContainer");
const favoritesContainer = document.getElementById("favoritesContainer");
const searchInput = document.getElementById("searchInput");
const cuisineSelect = document.getElementById("cuisine");
const areaSelect = document.getElementById("area");
const ambienceSelect = document.getElementById("ambience");
const priceSelect = document.getElementById("price");
const sortSelect = document.getElementById("sort");
const resultsSummary = document.getElementById("resultsSummary");
const toast = document.getElementById("toast");

let toastTimer;
let lastFocusedElement;

function showToast(message, isError = false) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.toggle("toast-error", isError);
    toast.classList.add("toast-visible");
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => toast.classList.remove("toast-visible"), 3200);
}

function readStorage(key, fallback) {
    try {
        const stored = localStorage.getItem(key);
        return stored === null ? fallback : JSON.parse(stored);
    } catch (error) {
        console.error(`Unable to read ${key} from local storage.`, error);
        showToast("Your saved data could not be loaded in this browser.", true);
        return fallback;
    }
}

function writeStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
    } catch (error) {
        console.error(`Unable to save ${key} to local storage.`, error);
        showToast("Your change could not be saved in this browser.", true);
        return false;
    }
}

function getFavorites() {
    const stored = readStorage("favourites", []);
    return Array.isArray(stored) ? stored : [];
}

function createTextElement(tagName, className, text) {
    const element = document.createElement(tagName);
    if (className) element.className = className;
    element.textContent = text;
    return element;
}

function getMapsUrl(restaurant) {
    return restaurant.maps || `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
        `${restaurant.name}, ${restaurant.area}, Bengaluru`
    )}`;
}

function showMap(restaurant) {
    let modal = document.getElementById("mapModal");
    if (!modal) {
        modal = document.createElement("div");
        modal.id = "mapModal";
        modal.className = "map-modal";
        modal.setAttribute("aria-hidden", "true");
        modal.innerHTML = `
            <div class="map-modal-backdrop" data-close-map></div>
            <div class="map-modal-dialog" role="dialog" aria-modal="true" aria-labelledby="mapModalTitle">
                <div class="map-modal-header">
                    <div>
                        <h3 id="mapModalTitle"></h3>
                        <p class="map-modal-sub"></p>
                    </div>
                    <button class="map-modal-close" type="button" aria-label="Close map" data-close-map>×</button>
                </div>
                <div class="map-modal-body"></div>
                <div class="map-modal-footer">
                    <span class="map-modal-info">Google Maps · Bengaluru</span>
                    <a class="map-button" target="_blank" rel="noopener noreferrer">Open in Google Maps ↗</a>
                </div>
            </div>`;
        document.body.appendChild(modal);
        modal.addEventListener("click", event => {
            if (event.target instanceof Element && event.target.closest("[data-close-map]")) {
                closeMap();
            }
        });
    }

    const title = modal.querySelector("#mapModalTitle");
    const subtitle = modal.querySelector(".map-modal-sub");
    const body = modal.querySelector(".map-modal-body");
    const externalLink = modal.querySelector(".map-modal-footer a");
    if (!title || !subtitle || !body || !(externalLink instanceof HTMLAnchorElement)) return;

    title.textContent = restaurant.name;
    subtitle.textContent = `${restaurant.area}, Bengaluru`;
    externalLink.href = getMapsUrl(restaurant);
    body.replaceChildren();

    const iframe = document.createElement("iframe");
    iframe.title = `Google Maps location for ${restaurant.name}`;
    iframe.src = restaurant.maps_embed || `https://maps.google.com/maps?q=${encodeURIComponent(
        `${restaurant.name}, ${restaurant.area}, Bengaluru`
    )}&z=15&output=embed`;
    iframe.loading = "lazy";
    iframe.referrerPolicy = "strict-origin-when-cross-origin";
    iframe.allowFullscreen = true;
    body.appendChild(iframe);

    lastFocusedElement = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    modal.setAttribute("aria-hidden", "false");
    modal.classList.add("open");
    document.body.style.overflow = "hidden";
    modal.querySelector(".map-modal-close")?.focus();
}

function closeMap() {
    const modal = document.getElementById("mapModal");
    if (!modal) return;
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    lastFocusedElement?.focus();
}

function createRestaurantCard(restaurant) {
    const card = document.createElement("article");
    card.className = "card";

    const photo = document.createElement("div");
    photo.className = "card-photo";
    const image = document.createElement("img");
    image.src = restaurant.image;
    image.alt = `${restaurant.name} in ${restaurant.area}`;
    image.loading = "lazy";
    image.addEventListener("error", () => {
        photo.replaceChildren(createTextElement("span", "empty-state", "Photo unavailable"));
    }, { once: true });
    photo.appendChild(image);

    if (restaurant.photo_verified) {
        photo.appendChild(createTextElement("span", "photo-verified-badge", "Real venue photo"));
    }

    const content = document.createElement("div");
    content.className = "card-content";

    const topline = document.createElement("div");
    topline.className = "card-topline";
    topline.append(
        createTextElement("span", "cuisine-label", restaurant.cuisine),
        createTextElement("span", "price-label", restaurant.price)
    );

    const name = createTextElement("h3", "", restaurant.name);
    const location = createTextElement("p", "card-location", `📍 ${restaurant.area}`);
    const details = document.createElement("div");
    details.className = "card-details";
    details.append(
        createTextElement("span", "", restaurant.ambience),
        createTextElement("span", "", `★ ${restaurant.rating}/10`)
    );

    const actions = document.createElement("div");
    actions.className = "card-actions";

    const mapPreviewButton = createTextElement("button", "map-preview-btn", "Preview map");
    mapPreviewButton.type = "button";
    mapPreviewButton.dataset.mapPreview = String(restaurant.id);

    const mapLink = createTextElement("a", "map-button", "Google Maps ↗");
    mapLink.href = getMapsUrl(restaurant);
    mapLink.target = "_blank";
    mapLink.rel = "noopener noreferrer";

    const isFavorite = getFavorites().includes(restaurant.id);
    const favoriteButton = createTextElement("button", "favorite-button", isFavorite ? "♥ Saved" : "♡ Save");
    favoriteButton.type = "button";
    favoriteButton.dataset.favorite = String(restaurant.id);
    favoriteButton.setAttribute("aria-pressed", String(isFavorite));
    favoriteButton.setAttribute("aria-label", `${isFavorite ? "Remove" : "Save"} ${restaurant.name} ${isFavorite ? "from" : "to"} favourites`);

    actions.append(mapPreviewButton, mapLink, favoriteButton);
    content.append(topline, name, location, details, actions);
    card.append(photo, content);
    return card;
}

function renderRestaurants(data, target) {
    target.replaceChildren();
    if (data.length === 0) {
        target.appendChild(createTextElement("p", "empty-state", "No places match just yet. Try changing a filter."));
        return;
    }
    data.forEach(restaurant => target.appendChild(createRestaurantCard(restaurant)));
}

function getFilteredRestaurants() {
    const query = searchInput.value.trim().toLocaleLowerCase();
    const filtered = restaurants.filter(restaurant => {
        const matchesQuery = !query || [
            restaurant.name,
            restaurant.cuisine,
            restaurant.area,
            restaurant.ambience
        ].some(value => value.toLocaleLowerCase().includes(query));
        return matchesQuery
            && (!cuisineSelect.value || restaurant.cuisine === cuisineSelect.value)
            && (!areaSelect.value || restaurant.area === areaSelect.value)
            && (!ambienceSelect.value || restaurant.ambience === ambienceSelect.value)
            && (!priceSelect.value || restaurant.price === priceSelect.value);
    });

    if (sortSelect.value === "rating") {
        filtered.sort((first, second) => second.rating - first.rating);
    } else if (sortSelect.value === "name") {
        filtered.sort((first, second) => first.name.localeCompare(second.name));
    }
    return filtered;
}

function searchRestaurants() {
    const results = getFilteredRestaurants();
    renderRestaurants(results, restaurantContainer);
    resultsSummary.textContent = `${results.length} ${results.length === 1 ? "lovely place" : "lovely places"} to explore`;
}

function renderFavorites() {
    const favoriteIds = getFavorites();
    const favoriteRestaurants = restaurants.filter(restaurant => favoriteIds.includes(restaurant.id));
    renderRestaurants(favoriteRestaurants, favoritesContainer);
}

function toggleFavorite(id) {
    const favorites = getFavorites();
    const alreadySaved = favorites.includes(id);
    const updated = alreadySaved ? favorites.filter(favoriteId => favoriteId !== id) : [...favorites, id];
    if (!writeStorage("favourites", updated)) return;
    renderFavorites();
    searchRestaurants();
    renderRestaurants([...restaurants].sort((a, b) => b.rating - a.rating).slice(0, 6), featuredContainer);
    showToast(alreadySaved ? "Removed from your favourites." : "Saved to your favourites.");
}

function renderReviews() {
    const reviews = readStorage("reviews", []);
    const container = document.getElementById("reviews");
    container.replaceChildren();
    if (!Array.isArray(reviews) || reviews.length === 0) {
        container.appendChild(createTextElement("p", "empty-state", "Be the first to leave a little love."));
        return;
    }

    reviews.slice().reverse().forEach(review => {
        const item = document.createElement("article");
        item.className = "review";
        item.append(
            createTextElement("h3", "", review.name),
            createTextElement("p", "review-byline", review.restaurantName || "Nibbl diner"),
            createTextElement("span", "review-rating", `★ ${review.overall}/5 overall`),
            createTextElement("p", "", `Food ${review.food}/5 · Ambience ${review.ambience}/5`),
            createTextElement("p", "review-copy", review.review)
        );
        container.appendChild(item);
    });
}

function renderFeedback() {
    const feedback = readStorage("feedback", []);
    const container = document.getElementById("feedbackList");
    container.replaceChildren();
    if (!Array.isArray(feedback) || feedback.length === 0) {
        container.appendChild(createTextElement("p", "empty-state", "Your feedback will help make Nibbl even better."));
        return;
    }

    feedback.slice().reverse().forEach(entry => {
        const item = document.createElement("article");
        item.className = "review";
        item.append(
            createTextElement("h3", "", entry.name),
            createTextElement("span", "review-rating", `★ ${entry.rating}/5 Nibbl experience`),
            createTextElement("p", "review-copy", entry.feedback)
        );
        container.appendChild(item);
    });
}

if (!Array.isArray(restaurants) || restaurants.length === 0) {
    console.error("The restaurant catalog did not load.");
    showToast("Restaurant data could not be loaded. Please refresh the page.", true);
} else {
    const featuredRestaurants = [...restaurants].sort((first, second) => second.rating - first.rating).slice(0, 6);
    renderRestaurants(featuredRestaurants, featuredContainer);
    searchRestaurants();
    renderFavorites();

    const heroPhotoWall = document.getElementById("heroPhotoWall");
    if (heroPhotoWall) {
        restaurants.filter(restaurant => restaurant.photo_verified).slice(0, 4).forEach((restaurant, index) => {
            const tile = document.createElement("figure");
            tile.className = "hero-photo-tile";
            const image = document.createElement("img");
            image.src = restaurant.image;
            image.alt = `${restaurant.name}, ${restaurant.area}`;
            image.loading = index === 0 ? "eager" : "lazy";
            tile.append(image, createTextElement("figcaption", "", `${restaurant.name} · ${restaurant.area}`));
            heroPhotoWall.appendChild(tile);
        });
    }

    const restaurantCount = document.getElementById("restaurantCount");
    const cuisineCount = document.getElementById("cuisineCount");
    const areaCount = document.getElementById("areaCount");
    if (restaurantCount) restaurantCount.textContent = String(restaurants.length);
    if (cuisineCount) cuisineCount.textContent = String(new Set(restaurants.map(restaurant => restaurant.cuisine)).size);
    if (areaCount) areaCount.textContent = String(new Set(restaurants.map(restaurant => restaurant.area)).size);

    const reviewSelect = document.getElementById("reviewRestaurant");
    restaurants.forEach(restaurant => {
        const option = document.createElement("option");
        option.value = String(restaurant.id);
        option.textContent = restaurant.name;
        reviewSelect.appendChild(option);
    });
}

document.getElementById("searchBtn").addEventListener("click", searchRestaurants);
document.getElementById("clearFiltersBtn").addEventListener("click", () => {
    searchInput.value = "";
    cuisineSelect.value = "";
    areaSelect.value = "";
    ambienceSelect.value = "";
    priceSelect.value = "";
    sortSelect.value = "recommended";
    searchRestaurants();
});

document.getElementById("randomBtn").addEventListener("click", () => {
    const candidates = getFilteredRestaurants();
    if (candidates.length === 0) {
        showToast("No places match these filters. Try clearing one.", true);
        return;
    }
    const pick = candidates[Math.floor(Math.random() * candidates.length)];
    renderRestaurants([pick], restaurantContainer);
    resultsSummary.textContent = `Your surprise pick: ${pick.name} in ${pick.area}`;
});

searchInput.addEventListener("input", searchRestaurants);
document.getElementById("viewFavoritesBtn").addEventListener("click", () => {
    renderFavorites();
    document.getElementById("favorites").scrollIntoView({ behavior: "smooth" });
});

[restaurantContainer, featuredContainer, favoritesContainer].forEach(container => {
    container.addEventListener("click", event => {
        if (!(event.target instanceof Element)) return;
        const mapButton = event.target.closest("[data-map-preview]");
        if (mapButton) {
            const restaurant = restaurants.find(item => item.id === Number(mapButton.dataset.mapPreview));
            if (restaurant) showMap(restaurant);
            return;
        }

        const favoriteButton = event.target.closest("[data-favorite]");
        if (favoriteButton) toggleFavorite(Number(favoriteButton.dataset.favorite));
    });
});

document.addEventListener("keydown", event => {
    if (event.key === "Escape") closeMap();
});

document.querySelectorAll(".cuisine-card").forEach(card => {
    const applyCuisine = () => {
        cuisineSelect.value = card.dataset.cuisine;
        searchRestaurants();
        document.getElementById("finder").scrollIntoView({ behavior: "smooth" });
    };
    card.addEventListener("click", applyCuisine);
    card.addEventListener("keydown", event => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            applyCuisine();
        }
    });
});

const themeButton = document.getElementById("themeBtn");
const savedTheme = readStorage("theme", "light");
if (savedTheme === "dark") document.body.classList.add("dark-theme");

function updateThemeButton() {
    const isDark = document.body.classList.contains("dark-theme");
    themeButton.textContent = isDark ? "☾" : "☼";
    themeButton.setAttribute("aria-label", `Switch to ${isDark ? "light" : "dark"} mode`);
}

updateThemeButton();
themeButton.addEventListener("click", () => {
    document.body.classList.toggle("dark-theme");
    updateThemeButton();
    writeStorage("theme", document.body.classList.contains("dark-theme") ? "dark" : "light");
});

document.getElementById("ratingForm").addEventListener("submit", event => {
    event.preventDefault();
    const form = event.currentTarget;
    const restaurant = restaurants.find(item => item.id === Number(document.getElementById("reviewRestaurant").value));
    if (!restaurant) {
        showToast("Choose a restaurant before submitting your review.", true);
        return;
    }

    const review = {
        restaurantName: restaurant.name,
        name: document.getElementById("reviewName").value.trim(),
        food: Number(document.getElementById("foodRating").value),
        ambience: Number(document.getElementById("ambienceRating").value),
        overall: Number(document.getElementById("overallRating").value),
        review: document.getElementById("review").value.trim(),
        date: new Date().toISOString()
    };
    const reviews = readStorage("reviews", []);
    if (!Array.isArray(reviews)) {
        showToast("Saved reviews could not be read. Please clear the invalid browser data.", true);
        return;
    }
    if (!writeStorage("reviews", [...reviews, review])) return;
    form.reset();
    renderReviews();
    showToast("Thank you for sharing your review!");
});

document.getElementById("feedbackForm").addEventListener("submit", event => {
    event.preventDefault();
    const form = event.currentTarget;
    const feedback = {
        name: document.getElementById("feedbackName").value.trim(),
        email: document.getElementById("feedbackEmail").value.trim(),
        rating: Number(document.getElementById("feedbackRating").value),
        feedback: document.getElementById("feedbackText").value.trim(),
        date: new Date().toISOString()
    };
    const entries = readStorage("feedback", []);
    if (!Array.isArray(entries)) {
        showToast("Saved feedback could not be read. Please clear the invalid browser data.", true);
        return;
    }
    if (!writeStorage("feedback", [...entries, feedback])) return;
    form.reset();
    renderFeedback();
    showToast("Thanks for helping us make Nibbl better!");
});

renderReviews();
renderFeedback();

const backToTop = document.getElementById("backToTop");
backToTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
window.addEventListener("scroll", () => {
    backToTop.classList.toggle("visible", window.scrollY > 300);
});

const loader = document.getElementById("loader");
window.addEventListener("load", () => {
    loader.classList.add("hidden");
    window.setTimeout(() => loader.remove(), 500);
}, { once: true });
})();
