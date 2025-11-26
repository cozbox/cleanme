# Quick Start: CleanMe Dashboard Installation

Follow these steps to get your CleanMe dashboard working:

## Step 1: Install Custom Card (Required)

The CleanMe dashboard requires Bubble Card from HACS:

### Bubble Card
1. Open HACS in Home Assistant
2. Click "Frontend"
3. Click "+ Explore & Download Repositories"
4. Search for "Bubble Card"
5. Click "Bubble Card" by Clooos
6. Click "Download"
7. Restart Home Assistant

## Step 2: Configure CleanMe Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **CleanMe**
4. Follow the setup wizard:
   - Enter zone name (e.g., "Kitchen")
   - Select camera entity
   - Choose AI personality
   - Set pickiness level (1-5)
   - Set check frequency
   - Enter Gemini API key
5. Click **Submit**

## Step 3: Access Your Dashboard

### Option A: Add Dashboard to Sidebar
After adding your first zone, CleanMe creates a dashboard file:
1. Go to **Settings** → **Dashboards**
2. Click **Add Dashboard**
3. Choose **Use YAML**
4. Select `/config/dashboards/cleanme.yaml`
5. Give it a title: "CleanMe"
6. Done! 🎉

### Option B: YAML Mode Setup
If you use YAML mode for dashboards:

1. **Add to configuration.yaml:**
   ```yaml
   lovelace:
     dashboards:
       cleanme-dashboard:
         mode: yaml
         title: CleanMe
         icon: mdi:broom
         show_in_sidebar: true
         filename: dashboards/cleanme.yaml
   ```

2. **Restart Home Assistant**

3. **Dashboard appears automatically** at `/config/dashboards/cleanme.yaml`

### Option C: Manual Setup
Copy dashboard cards manually:

1. **Generate dashboard:**
   ```yaml
   service: cleanme.regenerate_dashboard
   ```

2. **Find generated YAML** at `/config/dashboards/cleanme.yaml`

3. **Copy cards** to your existing dashboard

## Step 4: Verify Dashboard Works

Your dashboard should show:
- ✅ Zone status (tidy/messy) with colored icons
- ✅ Task count badge
- ✅ AI comment
- ✅ Last check timestamp
- ✅ Buttons to check, mark done, snooze

### Troubleshooting

**Dashboard not showing?**
- Restart Home Assistant after installing custom cards
- Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- Check logs: Settings → System → Logs

**"Custom element doesn't exist" error?**
- Bubble Card not installed
- Install via HACS (see Step 1)
- Restart Home Assistant
- Clear browser cache

**Cards show wrong data?**
- Check entity names in Settings → Devices & Services → Entities
- Entity names should match: `binary_sensor.{zone}_tidy`
- Try regenerating: `service: cleanme.regenerate_dashboard`

**Dashboard file not created?**
- Check `/config/dashboards/` directory exists
- Check logs in `/config/cleanme.log`
- Create directory manually: `mkdir /config/dashboards`
- Try: `service: cleanme.regenerate_dashboard`

## Step 5: Add More Zones (Optional)

Repeat Step 2 to add more rooms:
- Living Room
- Bedroom
- Bathroom
- Office
- etc.

The dashboard automatically updates with each new zone!

## Quick Reference

| Task | Service Call |
|------|--------------|
| Regenerate dashboard | `cleanme.regenerate_dashboard` |
| Check a zone | `cleanme.request_check` (zone: "Kitchen") |
| Mark zone as done | `cleanme.clear_tasks` (zone: "Kitchen") |
| Snooze zone | `cleanme.snooze_zone` (zone: "Kitchen", duration_minutes: 60) |

## File Locations

- Dashboard YAML: `/config/dashboards/cleanme.yaml`
- Integration logs: `/config/cleanme.log`
- Example files: `/config/custom_components/cleanme/examples/`

## Need More Help?

See the full guide: **DASHBOARD_SETUP.md**

Or open an issue: https://github.com/cozbox/cleanme/issues

---

**You did it! Time to start tracking your tidy zones! 🧹✨**
