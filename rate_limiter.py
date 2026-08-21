import redis


# ============================================================
# RATE LIMIT CONFIGURATION
# ============================================================

RATE_LIMIT = 10
WINDOW = 60


# ============================================================
# REDIS CONNECTION
# ============================================================

redis_client = redis.Redis(
    host="127.0.0.1",
    port=6379,
    db=0,
    decode_responses=True,
)


# ============================================================
# RATE LIMIT CHECK
# ============================================================

def is_allowed(client_ip):

    key = f"rate_limit:{client_ip}"

    # Increment request counter in Redis
    request_count = redis_client.incr(key)

    # First request → set 60-second expiry
    if request_count == 1:

        redis_client.expire(
            key,
            WINDOW
        )

    # Rate limit exceeded
    if request_count > RATE_LIMIT:

        return False

    return True