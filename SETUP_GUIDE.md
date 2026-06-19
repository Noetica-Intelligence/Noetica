# 🚀 Scientific Intelligence System — Setup Guide

Your system has been successfully upgraded to the **MVP Subscription Architecture**! It now supports reading subscriber preferences from Google Sheets and generating multiple personalized digests completely free.

Follow these steps to deploy your system to GitHub Actions.

## Step 1: Push Code to GitHub
Push the `scientific_intelligence` folder to a new private GitHub repository.

## Step 2: Set up Google Forms & Sheets
1. Create a **Google Form** with the exact fields described in your spec:
   * **Email Address** (Required)
   * **Name**
   * **Expertise Level** (Beginner / Intermediate / Advanced / Researcher / Industry Professional)
   * **Reading Time Per Day** (5 / 10 / 15 / 30 / 60 / 120 Minutes)
   * **Report Frequency** (Daily / Weekly / Monthly)
   * **Interests** (Checkboxes for fields)
   * **Discovery Preferences** (Checkboxes)
   * **Exploration Preference** (Yes / No)
   * **Consent** (Yes)
2. In the Responses tab, click **"Link to Sheets"**.
3. In the new Google Sheet, go to **File > Share > Publish to web**.
4. Select the specific Sheet containing the form responses, and change "Web page" to **"Comma-separated values (.csv)"**.
5. Click **Publish**. Copy the URL.
6. Extract the `GOOGLE_SHEET_ID` from the URL. It is the long string of characters between `/d/` and `/export`.

## Step 3: Set up Gmail App Password
1. Go to your Google Account > **Security**.
2. Ensure **2-Step Verification** is turned ON.
3. Search for **App passwords** in the top search bar.
4. Create a new App Password (name it "GitHub Actions").
5. Copy the generated 16-character password (do not include spaces).

## Step 4: Add GitHub Secrets
Go to your GitHub Repository > **Settings** > **Secrets and variables** > **Actions** > **New repository secret**.

Add the following exactly:

| Name | Value |
|---|---|
| `GMAIL_EMAIL` | Your Gmail address (e.g., `you@gmail.com`) |
| `GMAIL_APP_PASSWORD` | The 16-character password from Step 3 |
| `GOOGLE_SHEET_ID` | The ID of your published Google Sheet |

## Step 5: Test the Workflow
1. Go to the **Actions** tab in your repository.
2. Click **"🔬 Scientific Intelligence Daily Digest"** on the left.
3. Click **"Run workflow"** on the right.
4. Wait 1-2 minutes for the workflow to complete. It will fetch papers, read your Google Sheet, personalize the digests, and send the emails out!

---
*Note: The workflow is scheduled to run automatically every day at 08:00 UTC (13:30 IST). You can change this schedule in `.github/workflows/daily_report.yml`.*
