INSERT INTO users (username, email, password_hash, api_key)
VALUES
    ("user", "user@example.com", "pbkdf2:sha256:260000$YHcv5XMzQ3YSaPZc$ea146325db5e096d612e8f5d84e8319d42e8b9513971d9c265c7f8cdda0994d6", "ryEW79gxk4EUZsS305LcHa35mVeXqv3Q"); /* Password: password */

INSERT INTO files (anonymous, name, parent_id)
VALUES
	(false, "owned-self.txt", 1),
	(false, "owned-other.txt", 2),
	(true, "anonymous.txt", null);

INSERT INTO invites (active, parent_id, code, used)
VALUES
    (true, 1, "hjfv4Kmw1uQE77VmIVSDm178EIbTVsqh", false),  /* Valid */
    (true, 2, "QPPN41ePHKdC93C493tStVB5tFilsJ7B", false),  /* Valid (other owner) */
    (true, 1, "3ag25TZnKO3IumvbMaG6fZObYNGMlEsJ", true),   /* Used */
    (false, 1, "vOLeHOwoKO3mvOAbntO34odCvu57pgl7", false); /* Deleted */
