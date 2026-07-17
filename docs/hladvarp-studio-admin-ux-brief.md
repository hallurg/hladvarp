# Hladvarp Studio Admin UX Brief

Date: 2026-07-06
Status: `DESIGN APPROVED FOR STAGED IMPLEMENTATION`

## Decision

Hladvarp Studio should become more polished, guided, and owner-focused.

The customer should not land in a system-admin style dashboard with global totals for all podcasts, all users, all ads, or all platform objects.

Podcast owners should see:

- their own podcast
- their current plan / commercial status
- what they can do next
- limits that affect them
- simple actions for episodes, recording, publishing, RSS, cover/banner, and commercial-use declaration

System administrators should still have operational views for:

- all podcasts
- all users
- all applications
- ads
- categories
- distribution
- retention
- policy/plan administration

## Product Principle

The Studio should help people spend time on what matters:

- creating episodes
- understanding their podcast status
- publishing safely
- seeing what their subscription allows

It should not ask customers to understand the whole platform.

## Current UI Findings

The current Studio dashboard is built in:

- `/opt/hladvarp-custom/modules/HladvarpStudio/Controllers/StudioController.php`

Relevant methods:

- `index()`
- `podcasts()`
- `podcastForm()`
- `episodeForm()`
- `ads()`
- `studioCan()`
- `canManageStudioPermissions()`
- `studioPodcasts()`
- `findPodcastForStudio()`

Current owner-facing issues:

- dashboard cards show global counts such as total podcasts, total episodes, total users, total ads, categories, targets, and SEO profiles
- podcast/episode forms rely on large textareas
- forms feel like database administration rather than guided content editing
- subscription/commercial-use status is present only as low-level fields like `ads_enabled`, weekly quota, and billing profile
- owner and system-admin concerns are mixed in the same dashboard

## Launch Safety

Do not redesign the full Studio before public launch unless explicitly approved as a launch-blocking UX fix.

Reason:

- this touches login-adjacent and launch-critical workflows
- podcast edit, episode upload, ads, recorder links, and permission-specific visibility all live in one large controller
- there is no clean local Hladvarp source repository/branch baseline in the current workspace

Launch-safe work:

- document the desired UX
- keep current runtime stable
- avoid broad WYSIWYG/editor changes before launch
- after launch, implement in small reversible steps

## Recommended UX Model

### Owner Home

For a podcast owner, the first screen should be "Mitt hlaðvarp" rather than "Cayennepod Studio".

Suggested sections:

- podcast identity: title, handle, cover, status
- next action: record episode, upload episode, edit show page, copy RSS link
- plan/status: Free, Creator, Business, Enterprise, or manual review
- commercial-use status: no commercial use / declared commercial / needs review
- usage limits: episodes this week, weekly quota, ads allowed/not allowed
- publishing status: draft/published/paused/ended

Avoid global totals.

### Admin Home

For admins, keep an operational dashboard but separate it clearly from the owner experience.

Admin sections:

- applications needing review
- podcasts needing commercial review
- ads needing attention
- users and permissions
- retention and audit
- platform health links

### Guided Editing

Replace giant writing boxes over time with guided editing patterns:

- compact fields grouped by task
- progressive sections
- inline preview
- simple toolbar for formatting
- reusable content blocks where practical
- image/cover/banner previews
- status chips and toggles
- plan-aware feature hints

For descriptions, a future editor can support:

- headings
- bold / italic
- links
- lists
- preview of public podcast page text

Do not add a heavy WYSIWYG editor until it is tested against Castopod markdown/RSS output.

### Plan-Aware UI

The UI should show features based on entitlement:

- Free: no ads/sponsorship controls, show commercial-use explanation
- Creator: ads/sponsorship controls visible
- Business: business controls visible only when implemented
- Enterprise: manual/custom status

Do not display planned-only features as if they are working.

## Staged Implementation

### Safe Now

- Keep existing admin UI behavior.
- Record this UX direction.
- Use manual admin communication for subscription/commercial status.

### First Post-Launch Patch

Small, reversible changes:

1. Split dashboard rendering:
   - owner dashboard for non-platform admins
   - operational dashboard for admins
2. Remove global counts from owner dashboard.
3. Show owner-specific podcast cards.
4. Add plan/commercial-use status summary using existing `ads_enabled` and weekly quota data.
5. Keep existing forms and routes intact.

### Second Patch

Improve form ergonomics:

1. Add cover/banner preview.
2. Reduce textarea height.
3. Add markdown preview for podcast and episode descriptions.
4. Add helper text based on plan/commercial status.
5. Improve actions and status chips.

### Third Patch

Introduce the subscription policy service:

1. centralize feature and limit checks
2. make UI plan-aware through the policy service
3. move ad and quota checks behind the service
4. add tests

### Later

Evaluate a lightweight editor after launch:

- markdown-first editor
- preview mode
- RSS-safe output
- no auto-formatting that damages feed content

## Acceptance Criteria

Owner dashboard:

- does not show global platform totals
- shows only the owner user's podcast(s)
- shows plan/commercial-use status
- shows quota status
- has clear next actions
- keeps existing podcast/episode workflows working

Admin dashboard:

- preserves operational visibility
- keeps application review, ads, users, retention, distribution, and SEO accessible

Safety:

- no payment integration
- no national registry verification claim
- no AI ad detection
- no broad launch-time rewrite
