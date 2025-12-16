import re

# Redis Keys
SEEN_ENDPOINTS_KEY_TPL = "js_endpoints:{host}"
CONTENT_HASH_KEY_TPL = "content_hashes:{hash}"
CHECKPOINT_KEY_TPL = "checkpoint:{cycle_id}"

# Defaults
DEFAULT_BATCH_SIZE = 1500
DEFAULT_RETRY_ATTEMPTS = 2
DEFAULT_RETRY_DELAY = 5
CONCURRENT_REQUESTS = 5
LARGE_FILE_THRESHOLD = 2_000_000  # 2MB
LARGE_FILE_TIMEOUT = 90
NORMAL_TIMEOUT = 30

# AI Server
AI_SERVER_URL = "http://localhost:8080/analyze"
# TODO: Move API Key to env var
AI_SERVER_API_KEY = "GPn4OnHcjdDRPVEu00HHBoRyU1PYN/3kgilKszC9fvs="

# Blocklists
SCRIPT_BLOCKLIST_DOMAINS = {
    # === GOOGLE ECOSYSTEM ===
    "google-analytics.com", "googletagmanager.com", 
    "googleads.g.doubleclick.net", "googlesyndication.com",
    "googleadservices.com", "adservice.google.com",
    "maps.googleapis.com", "maps.google.com", "maps.gstatic.com",
    "fonts.googleapis.com", "fonts.gstatic.com",
    "firebase.googleapis.com", "firebaseapp.com", "firebaseio.com",
    "recaptcha.net", "gstatic.com", "ggpht.com",
    
    # === FACEBOOK/META ===
    "connect.facebook.net", "facebook.com", "fbcdn.net",
    "instagram.com", "cdninstagram.com",
    
    # === ADVERTISING & TRACKING ===
    "adroll.com", "criteo.com", "doubleclick.net",
    "taboola.com", "outbrain.com", "admixer.net",
    "pubmatic.com", "rubiconproject.com", "openx.net",
    "adsrvr.org", "adnxs.com", "advertising.com",
    "scorecardresearch.com", "comscore.com",
    "quantserve.com", "quantcount.com",
    "mixpanel.com", "segment.com", "segment.io",
    "mookie1.com", "krxd.net", "rlcdn.com",
    "bluekai.com", "exelator.com", "eyeota.net",
    
    # === SOCIAL MEDIA ===
    "twitter.com", "twimg.com", "t.co",
    "pinterest.com", "pinimg.com",
    "linkedin.com", "licdn.com",
    "tiktok.com", "tiktokcdn.com",
    "snapchat.com", "sc-cdn.net",
    "reddit.com", "redd.it", "redditstatic.com",
    
    # === CDN & INFRASTRUCTURE ===
    "cdn.optimizely.com", "optimizely.com",
    "cloudflare.com", "cloudflareinsights.com",
    "akamaihd.net", "akamaized.net", "akstat.io",
    "fastly.net", "fastly-insights.com",
    "jsdelivr.net", "unpkg.com", "cdnjs.cloudflare.com",
    
    # === ANALYTICS ===
    "hotjar.com", "hotjar.io",
    "clarity.ms", "c.clarity.ms",
    "amplitude.com", "cdn.amplitude.com",
    "fullstory.com", "fs.com",
    "mouseflow.com", "logrocket.com",
    "heap.io", "heapanalytics.com",
    "newrelic.com", "nr-data.net",
    "sentry.io", "sentry-cdn.com",
    
    # === VIDEO ===
    "youtube.com", "ytimg.com", "googlevideo.com",
    "vimeo.com", "vimeocdn.com",
    "wistia.com", "wistia.net",
    "brightcove.com", "bcove.com",
    
    # === CHAT & SUPPORT ===
    "intercom.io", "intercom.com", "intercomcdn.com",
    "zendesk.com", "zdassets.com",
    "livechat.com", "livechatinc.com",
    "drift.com", "driftt.com",
    "tawk.to", "embed.tawk.to",
    "crisp.chat", "client.crisp.chat",
    
    # === EMAIL & MARKETING ===
    "mailchimp.com", "list-manage.com",
    "sendgrid.com", "sendgrid.net",
    "hubspot.com", "hs-scripts.com", "hsforms.com",
    "marketo.com", "marketo.net", "mktoresp.com",
    "pardot.com", "salesforce.com", "force.com",
    
    # === MAPS (except Google) ===
    "mapbox.com", "mapbox.gl",
    "here.com", "heremaps.com",
    "openstreetmap.org", "tile.openstreetmap.org",
    
    # === LOCALIZATION ===
    "crowdin.com", "transifex.com",
    "phrase.com", "phraseapp.com",
    
    # === ADOBE ===
    "adobedtm.com", "adobe.com", "omtrdc.net",
    "demdex.net", "everesttech.net",
    "2o7.net", "omniture.com",
    
    # === BOOKING/AIRBNB SPECIFIC ===
    "muscache.com",  # Airbnb CDN

    # === OTHER COMMON ===
    "trustpilot.com", "tp.media",
    "cookielaw.org", "onetrust.com",
    "evidon.com", "ghostery.com",
    "jsdelivr.net", "bootstrapcdn.com",
    "jquery.com", "code.jquery.com",
    
    # === A/B TESTING & FEATURE FLAGS ===
    "launchdarkly.com", "app.launchdarkly.com",
    "split.io", "cdn.split.io",
    "optimizely.com", "cdn.optimizely.com",
    "growthbook.io", "cdn.growthbook.io",
    "unleash.io", "unleash-proxy.io",
    "flagsmith.com", "edge.flagsmith.com",
    
    # === ERROR TRACKING (расширение) ===
    "bugsnag.com", "notify.bugsnag.com",
    "rollbar.com", "cdn.rollbar.com",
    "airbrake.io", "airbrake-js.s3.amazonaws.com",
    "raygun.com", "cdn.raygun.io",
    "trackjs.com", "cdn.trackjs.com",
    
    # === SESSION REPLAY ===
    "smartlook.com", "rec.smartlook.com",
    "inspectlet.com", "cdn.inspectlet.com",
    "luckyorange.com", "cdn.luckyorange.com",
    "sessioncam.com", "d2oh4tlt9mrke9.cloudfront.net",
    "crazyegg.com", "script.crazyegg.com",
    
    # === HEATMAPS ===
    "clicktale.net", "cdn.clicktale.net",
    "ptengine.com", "cdn.ptengine.com",
    
    # === PUSH NOTIFICATIONS ===
    "onesignal.com", "cdn.onesignal.com",
    "pushwoosh.com", "cp.pushwoosh.com",
    "pusher.com", "js.pusher.com",
    "ably.io", "cdn.ably.io",
    
    # === CONSENT MANAGEMENT (расширение) ===
    "cookiepro.com", "cookie-cdn.cookiepro.com",
    "trustarc.com", "consent.trustarc.com",
    "usercentrics.com", "app.usercentrics.eu",
    "iubenda.com", "cdn.iubenda.com",
    
    # === BOT DETECTION ===
    "px-cdn.net", "client.px-cdn.net",  # PerimeterX
    "datadome.co", "js.datadome.co",
    "shape.security", "cdn.shape.security",
    "kasada.io",
    
    # === CONVERSION TRACKING ===
    "branch.io", "cdn.branch.io",
    "adjust.com", "app.adjust.com",
    "appsflyer.com", "web-sdk.appsflyer.com",
    
    # === CDN PROVIDERS ===
    "bunnycdn.com",
    "keycdn.com",
    "stackpath.com", "stackpathcdn.com",
    
    # === PAYMENT GATEWAYS (расширение) ===
    "adyen.com", "checkoutshopper-live.adyen.com",
    "klarna.com", "x.klarnacdn.net",
    "afterpay.com", "portal.afterpay.com",
    "affirm.com", "cdn1.affirm.com",
    
    # === AUTHENTICATION (OAuth) ===
    "auth0.com", "cdn.auth0.com",
    "okta.com", "global.oktacdn.com",
    "loginradius.com", "hub.loginradius.com",
    
    # === CMS/WEBSITE BUILDERS ===
    "wixstatic.com", "static.wixstatic.com",
    "squarespace.com", "assets.squarespace.com",
    "webflow.com", "assets.website-files.com",
    "shopify.com", "cdn.shopify.com",
    "wordpress.com", "s0.wp.com",
}

JS_FILENAME_BLACKLIST_PATTERNS = {
    # === ANALYTICS & TRACKING ===
    'gtag', 'gtm', 'ga.js', 'analytics', 
    'segment', 'mixpanel', 'amplitude',
    'hotjar', 'clarity', 'fullstory', 'logrocket',
    'mouseflow', 'heap', 'newrelic', 'sentry',
    'datadog', 'comscore', 'quantcast',
    'yandex', 'metrika', 'top.mail',
    
    # === MAPS ===
    'google.maps', 'maps.googleapis', 'mapbox',
    'leaflet', 'mapsjs', 'geocoder',
    
    # === ADVERTISING ===
    'doubleclick', 'googlesyndication', 'googleads',
    'adroll', 'criteo', 'taboola', 'outbrain',
    'adsense', 'adserver',
    
    # === SOCIAL MEDIA ===
    'facebook', 'fbevents', 'connect.facebook',
    'twitter', 'tweet', 'pinterest', 'linkedin',
    'instagram', 'tiktok', 'share-button',
    
    # === PAYMENTS ===
    'stripe', 'paypal', 'braintree', 'square',
    
    # === CHAT ===
    'intercom', 'zendesk', 'livechat', 'drift',
    'tawk', 'crisp',
    
    # === VIDEO ===
    'youtube', 'vimeo', 'wistia', 'brightcove',
    'jwplayer', 'videojs',
    
    # === CDN LIBRARIES ===
    'jquery', 'bootstrap', 'react.production.min',
    'vue.runtime', 'angular.min', 'lodash',
    'axios.min', 'polyfill',
    
    # === FONTS ===
    'fonts.googleapis', 'typekit', 'fontawesome',
    'webfont',
    
    # === COOKIE CONSENT ===
    'cookiebot', 'onetrust', 'cookielaw',
    
    # === RECAPTCHA ===
    'recaptcha', 'hcaptcha',
    
    # === LAZY-LOAD SPECIFIC ===
    'vendors~', 'vendor-', 'node_modules',
    'polyfill', 'legacy', 'compat', 'shim',
    'i18n', 'locale', 'lang-', 'translation',
    'runtime.', 'manifest.',
    
    # === SERVICE WORKER LIBS ===
    'workbox', 'sw-toolbox', 'serviceworker-',
    'firebase-messaging', 'push-notification',
    
    # === GRAPHQL CODEGEN ===
    '.generated.', '__generated__', 'graphql.schema',
    'apollo.config', 'relay.runtime',
    
    # === A/B TESTING ===
    'launchdarkly', 'split.io', 'optimizely',
    'experiment', 'feature-flag', 'growthbook',
    
    # === BOT DETECTION ===
    'perimeterx', 'px-client', 'datadome',
    'kasada', 'shape-defense',
    
    # === SESSION REPLAY ===
    'smartlook', 'inspectlet', 'luckyorange',
    'sessioncam', 'crazyegg',
}

JS_FILENAME_BLACKLIST_REGEX = re.compile(
    '|'.join(re.escape(pattern) for pattern in JS_FILENAME_BLACKLIST_PATTERNS),
    re.IGNORECASE
)

KNOWN_FIRST_PARTY_CDN = {
    'yastatic.net': ['yandex.ru', 'yandex.com'],
    'bstatic.com': ['booking.com'],
}
