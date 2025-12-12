daemonize = false;

modules_enabled = {
    "roster", -- Allow users to have a roster. Recommended ;)
    "saslauth", -- Authentication for clients and servers. Recommended if you want to log in.
    "tls", -- Add support for secure TLS on c2s/s2s connections
    "dialback", -- s2s dialback support
    "disco", -- Service discovery
    "carbons", -- Keep multiple clients in sync
    "pep", -- Enables users to publish their avatar, mood, activity, playing music and more
    "private", -- Private XML storage (for room bookmarks, etc.)
    "blocklist", -- Allow users to block communications with other users
    "vcard4", -- User profiles (stored in PEP)
    "vcard_legacy", -- Conversion between legacy vCard and PEP Avatar, vcard
    "limits", -- Enable bandwidth limiting for XMPP connections
    "version", -- Replies to server version requests
    "uptime", -- Report how long server has been running
    "time", -- Let others know the time here on this server
    "ping", -- Replies to XMPP pings with pongs
    "register", -- Allow users to register on this server using a client and change passwords
    "mam", -- Store messages in an archive and allow users to access it
    "admin_adhoc", -- Allows administration via an XMPP client that supports ad-hoc commands
    "bookmarks", -- Conversion between different bookmarks formats
    "conversejs", -- Web client
    "privilege" --
}

allow_registration = true
c2s_require_encryption = false
s2s_require_encryption = false
s2s_secure_auth = false

pidfile = "/var/run/prosody/prosody.pid"

authentication = "internal_hashed"

archive_expires_after = "1w"

plugin_server = "https://modules.prosody.im/rocks/"

log = {{levels = {min = "debug"}, to = "console"}}

certificates = "certs"


VirtualHost "localhost"
    http_host = "localhost"

Component "upload.localhost" "http_file_share"

Component "rooms.localhost" "muc"
    muc_room_locking = false


VirtualHost "prosody"
    http_host = "prosody"

Component "upload.prosody" "http_file_share"

Component "rooms.prosody" "muc"
    muc_room_locking = false
