CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    total_cents BIGINT NOT NULL,
    state TEXT NOT NULL DEFAULT 'pending'
);
