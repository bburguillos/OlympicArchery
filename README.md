# 🏹 Olympic Archery — Road to Gold (Version 1)

A Streamlit classroom app for **Sports by the Numbers**. Uses the same 24 athletes and 72-arrow perfect-10 counts as the expanded Paris 2024 worksheet kit.

## Upload to GitHub / deploy on Streamlit Community Cloud

1. Create a new GitHub repository (for example `olympic-archery`).
2. Upload `app.py`, `athletes.csv`, `requirements.txt`, `.streamlit/config.toml`, and `.gitignore`, preserving paths. (Do not upload real secrets.)
3. Visit https://share.streamlit.io/ , select **Create app** / **Deploy**, choose the GitHub repo, branch `main`, main file path `app.py`.
4. In Streamlit Cloud's app **Settings → Secrets**, add:
   ```toml
   TEACHER_PIN = "choose-a-private-pin"
   ```
   Save and reboot the app when prompted. Keep the PIN private; don't commit `.streamlit/secrets.toml`.
5. Open the public app URL from a student device. Teacher view requires the PIN; students select **Student Training**.

For local testing (optional): `pip install -r requirements.txt` then `streamlit run app.py`. Put your private PIN in `.streamlit/secrets.toml` on your computer.

## What works now

- 24 countries with national flags, real athletes, and verified-from-worksheet perfect-10 counts.
- Each student's probability calculation is checked with a ±0.51 percentage-point rounding tolerance; incorrect answers do not alter underlying stats.
- Student training includes a prediction followed by 10 separately simulated arrows and reflection data.
- Teacher mode (PIN-protected) chooses 2–24 countries, runs one complete 20-arrow simulated championship, displays medals, breaks ties with sudden-death arrows, and exports a CSV scoreboard.

## Important Version 1 limits

- **No cross-device live leaderboard or student logins.** Students can practice on their own devices; the teacher runs a class championship on their own browser/Promethean board. A shared student-controlled championship will require durable online data storage (for example Supabase).
- **No persistent student record**: students transfer training results to the worksheet.
- **Simplified simulation**: each arrow is only a perfect 10 or not a perfect 10. A miss is not assigned an invented 0–9 ring score. Historic qualifying outcomes are not replayed.
- The athlete probabilities derive from one 72-arrow ranking round, which is a sample, not a fixed skill rating. Independence across shots is a deliberate classroom modeling assumption.
- PIN guards casual entry to teacher controls; it's not a full authentication system. Don't put sensitive student data into this version.

## Future Version 2

Optional game polish: animated target, sound-free suspense, country scouting calculator, guided comparison, group assignments and scoring explanations. Future shared leaderboard requires its own connected database.
