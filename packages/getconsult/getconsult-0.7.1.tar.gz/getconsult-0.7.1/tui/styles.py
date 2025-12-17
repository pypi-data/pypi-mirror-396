"""
CSS Styles for the Consult TUI
"""

APP_CSS = """
/* Ultra-modern Title Bar */
#title-bar {
    height: 1;
    background: #001100;
    color: #00ff41;
    text-align: center;
    text-style: bold;
    margin-bottom: 1;
}

/* Enhanced Header */
#enhanced-header {
    height: 1;
    background: #001a00;
    color: #44ff44;
    dock: top;
}

.header-segment {
    background: #002200;
    color: #66ff66;
    text-style: bold;
    padding: 0 1;
    margin: 0;
    height: 1;
}

.header-brand {
    background: #003300;
    color: #88ff88;
    text-style: bold;
}

.header-workflow {
    background: #002200;
    color: #66dd66;
}

.header-memory {
    background: #332200;
    color: #ffcc44;
}

.header-memory.high {
    background: #331100;
    color: #ffaa44;
}

.header-memory.critical {
    background: #330000;
    color: #ff6666;
}

.header-provider {
    background: #001122;
    color: #44aaff;
}


.header-segment.ready {
    background: #002200;
    color: #66ff66;
}

.header-segment.processing {
    background: #332200;
    color: #ffcc44;
}

.header-segment.error {
    background: #330000;
    color: #ff6666;
}

/* System Status Indicator */
.system-status {
    height: 1;
    background: #000000;
    border-bottom: solid #00ff41;
    text-align: center;
    color: #00ff41;
    text-style: bold;
}

.system-status.ready {
    background: #001a00;
    color: #44ff44;
}

.system-status.processing {
    background: #1a1000;
    color: #ffcc00;
}

.system-status.error {
    background: #1a0000;
    color: #ff6666;
}

#sidebar {
    width: 32;
    background: #000000;
    border-right: thick #00ff41;
    padding: 1;
}

/* Locked state - subtle visual indication that config is frozen during workflow */
#sidebar.locked {
    border-right: thick #333333;
}

#sidebar.locked .section-header {
    color: #336633;
    background: #001100;
    border-left: thick #224422;
}

#sidebar.locked .setting {
    color: #224422;
}

#sidebar.locked .key-hint {
    color: #223322;
}

#sidebar.locked .hotkey {
    color: #334433;
    background: #0a0a0a;
}

#chat-area {
    padding: 0 1 1 1;
    background: #000000;
    height: 100%;
}


#messages-scroll {
    height: 1fr;
    border: solid #003311;
    background: #000000;
    margin-bottom: 1;
    scrollbar-background: #000000;
    scrollbar-color: #003311;
    scrollbar-size: 2 1;
}

.markdown-content {
    padding: 1;
    width: 100%;
}

/* ============================================
   INPUT AREA - Polished Query Entry
   ============================================ */

/* Input Section Container - Cohesive bordered unit */
#input-section {
    height: auto;
    background: #000a00;
    border: solid #004400;
    border-title-color: #00ff41;
    border-title-style: bold;
    border-subtitle-color: #666666;
    margin: 0;
    padding: 0;
}

#input-section.collapsed {
    display: none;
}

#input-section.expanded #chat-input {
    height: 10;
}

/* Processing state - frozen with visual feedback */
#input-section.processing {
    border: solid #333300;
    border-title-color: #ffcc00;
}

#input-section.processing #chat-input {
    background: #0a0a00;
    color: #666644;
}

#input-section.processing #send-btn {
    background: #332200;
    color: #ffcc00;
    border: solid #ffaa00;
}

#input-area {
    height: auto;
    padding: 1;
    background: #000a00;
}

#chat-input {
    width: 1fr;
    height: 3;
    background: #001100;
    border: none;
    color: #00ff41;
}

#chat-input:focus {
    background: #001a00;
}

#chat-input .text-area--cursor {
    background: #00ff41;
}

#send-btn {
    width: 12;
    height: 3;
    margin-left: 1;
    background: #003300;
    color: #00ff41;
    text-style: bold;
    border: solid #00ff41;
}

#send-btn:hover {
    background: #004400;
    color: #44ff44;
}

#send-btn.processing {
    background: #332200;
    color: #ffcc00;
    border: solid #ffaa00;
}

/* Information hierarchy */
.main-header {
    color: #00ffff;
    text-style: bold;
    margin: 1 0 0 0;
    padding: 1;
    background: #003333;
    border: solid #006666;
    text-align: center;
}

/* Section headers */
.section-header {
    color: #66ff66;
    text-style: bold;
    margin: 1 0 0 0;
    padding: 0 1;
    background: #002200;
    border-left: thick #44cc44;
    border-bottom: solid #224422;
}

/* Interactive settings */
.setting {
    color: #22cc55;
    padding: 0 2;
    margin: 0;
    height: 1;
    background: transparent;
}

.setting:hover {
    background: #002200;
    border-left: solid #44ff44;
    color: #44ff44;
    padding-left: 1;
}

.setting.changing {
    background: #003300;
    color: #66ff88;
    border-left: thick #66ff88;
    padding-left: 0;
}

.setting.critical {
    background: #220000;
    border-left: solid #ff4444;
}

.setting-label {
    color: #44aa66;
}

.setting-value {
    color: #88ff88;
    text-style: bold;
}

.setting-value.active {
    color: #aaffaa;
    text-style: bold;
    background: #003300;
    padding: 0 1;
}

.toggle-on {
    color: #88ff88;
    text-style: bold;
    background: #002200;
    padding: 0 1;
}

.toggle-off {
    color: #556655;
    background: #1a1a1a;
    padding: 0 1;
}

/* Memory status with prominence */
.memory-high {
    background: #332200;
    border-left: thick #ffcc00;
    color: #ffdd44;
}

.memory-critical {
    background: #331100;
    border-left: thick #ff6666;
    color: #ff8888;
}

/* Expert selection - right side panel */
#expert-modal {
    display: none;
    dock: right;
    width: 40%;
    height: 100%;
    background: #000000;
    border-left: thick #00ff41;
    padding: 1;
}

#expert-modal.show {
    display: block;
}

.expert-container {
    height: 100%;
    overflow-y: auto;
    background: #000000;
    padding: 1;
}

.expert-header {
    color: #00ff41;
    text-style: bold;
    text-align: center;
    border-bottom: solid #00ff41;
    padding-bottom: 1;
    margin-bottom: 1;
}

.expert-item {
    padding: 0 1;
    height: 1;
}

.expert-item.selected {
    color: #44ff44;
    text-style: bold;
}

.expert-item.unselected {
    color: #336633;
}

.expert-item:hover {
    background: #001100;
}

/* File browser - right side panel */
#file-modal {
    display: none;
    dock: right;
    width: 50%;
    height: 100%;
    background: #000000;
    border-left: thick #00ff41;
    padding: 1;
}

#file-modal.show {
    display: block;
}

.file-container {
    height: 100%;
    overflow-y: auto;
    background: #000000;
    padding: 1;
}

.file-header {
    color: #00ff41;
    text-style: bold;
    text-align: center;
    border-bottom: solid #00ff41;
    padding-bottom: 1;
    margin-bottom: 1;
}

.file-item {
    padding: 0 1;
    height: 1;
}

.file-item.directory {
    color: #00ff41;
    text-style: bold;
}

.file-item.file {
    color: #cccccc;
}

.file-item.supported {
    color: #44ff44;
}

.file-item:hover {
    background: #001100;
}

.file-path {
    color: #666666;
    text-style: italic;
    padding: 0 1;
    margin-bottom: 1;
}

/* Key hints */
.key-hint {
    color: #559955;
    text-align: left;
    padding: 0 2;
    margin: 0;
}

.hotkey {
    color: #88ff88;
    text-style: bold;
    background: #112211;
    padding: 0;
}

/* ============================================
   NEW COLLAPSIBLE WORKFLOW WIDGETS
   ============================================ */

/* WorkflowView - Main scrollable container */
#workflow-view {
    height: 1fr;
    padding: 1;
    background: #000000;
    border: solid #003311;
    margin-bottom: 1;
    scrollbar-background: #000000;
    scrollbar-color: #003311;
    scrollbar-size: 2 1;
}

/* Activity Log - chatty real-time insights area */
#system-messages {
    height: auto;
    min-height: 4;
    max-height: 12;
    background: #000800;
    border-top: solid #004411;
    border-left: thick #00ff41;
    padding: 0 1;
    scrollbar-background: #000000;
    scrollbar-color: #003311;
    scrollbar-size: 1 1;
}

/* Collapsed state - hide completely */
#system-messages.collapsed {
    display: none;
}

/* Collapsed bar - shown when log is hidden */
#log-collapsed-bar {
    display: none;
    height: 1;
    background: #001100;
    border-left: thick #336633;
    padding: 0 1;
    text-align: center;
}

#log-collapsed-bar.show {
    display: block;
}

/* Input area collapsed state */
#input-area.collapsed {
    display: none;
}

/* Collapsed input bar - shown when input is hidden */
#input-collapsed-bar {
    display: none;
    height: 1;
    background: #001111;
    border-left: thick #336666;
    padding: 0 1;
    text-align: center;
}

#input-collapsed-bar.show {
    display: block;
}

/* Detail Pane - full screen inspection mode (D to toggle) */
#detail-pane {
    display: none;
    dock: right;
    width: 100%;
    height: 100%;
    background: #000500;
    padding: 0;
}

#detail-pane.show {
    display: block;
}

#detail-content {
    padding: 0;
    color: #88ff88;
}

/* Status Header - always visible workflow state */
StatusHeader {
    height: 2;
    background: #001a00;
    border-bottom: solid #003311;
    padding: 0 1;
}

StatusHeader.active {
    background: #0a0f00;
    border-bottom: solid #00ff41;
}

StatusHeader .status-line {
    height: 1;
}

/* PhaseContainer - collapsible phase sections */
PhaseContainer {
    height: auto;
    margin: 0 0 1 0;
    border-left: thick #336633;
    padding: 0;
}

PhaseContainer.active {
    border-left: thick #ffcc00;
    background: #050a00;
}

PhaseContainer.complete {
    border-left: thick #00ff41;
}

PhaseContainer.pending {
    border-left: thick #333333;
}

PhaseContainer .phase-header {
    height: 1;
    padding: 0 1;
    background: #001100;
}

PhaseContainer .phase-header:hover {
    background: #002200;
}

PhaseContainer.active .phase-header {
    background: #0a0f00;
}

PhaseContainer .phase-content {
    padding: 0 0 0 2;
    height: auto;
}

PhaseContainer.-collapsed .phase-content {
    display: none;
}

/* AgentCard - collapsible response cards */
AgentCard {
    height: auto;
    margin: 0 0 0 1;
    border: solid #003311;
    padding: 0;
}

AgentCard.active {
    border: solid #ffcc00;
    background: #050800;
}

AgentCard .agent-header {
    height: 1;
    padding: 0 1;
    background: #001100;
}

AgentCard .agent-header:hover {
    background: #002200;
}

AgentCard.active .agent-header {
    background: #0a0800;
}

AgentCard .agent-content {
    padding: 1;
    height: auto;
}

AgentCard.-collapsed .agent-content {
    display: none;
}

/* ThinkingIndicator - current agent working */
ThinkingIndicator {
    height: 1;
    padding: 0 1 0 2;
    color: #ffcc00;
}

/* FeedbackGroup - collapsible feedback exchanges */
FeedbackGroup {
    height: auto;
    margin: 0 0 0 1;
    border: solid #333300;
    padding: 0;
}

FeedbackGroup .feedback-header {
    height: 1;
    padding: 0 1;
    background: #0a0a00;
}

FeedbackGroup .feedback-header:hover {
    background: #151500;
}

FeedbackGroup .feedback-content {
    padding: 1;
    height: auto;
}

FeedbackGroup.-collapsed .feedback-content {
    display: none;
}

/* FeedbackItem - individual feedback exchange */
FeedbackItem {
    height: auto;
    margin: 0 0 1 0;
    padding: 0;
}

/* IterationContainer - iteration within Phase 2 */
IterationContainer {
    height: auto;
    margin: 0 0 0 1;
    border-left: solid #333333;
    padding: 0;
}

IterationContainer.active {
    border-left: solid #ffcc00;
}

IterationContainer.complete {
    border-left: solid #00ff41;
}

IterationContainer .iteration-header {
    height: 1;
    padding: 0 1;
    background: #050505;
}

IterationContainer .iteration-header:hover {
    background: #101010;
}

IterationContainer .iteration-content {
    padding: 0 0 0 1;
    height: auto;
}

IterationContainer.-collapsed .iteration-content {
    display: none;
}

/* Welcome message in workflow view */
#welcome-container {
    padding: 2;
    text-align: center;
}

/* Query display - clean, minimal */
.query-display {
    margin: 0 0 1 0;
    padding: 1;
    background: #001a00;
    border-bottom: solid #003311;
}

/* ============================================
   DETAIL PANE - AGENT JOURNEY VISUALIZATION
   ============================================ */

/* Main Detail Pane Container */
DetailPane {
    height: 100%;
    padding: 0;
    background: #000500;
}

DetailPane .detail-header {
    height: 2;
    background: #001a00;
    border-bottom: solid #00ff41;
    padding: 0 1;
}

/* Consensus Trend Chart - at bottom of detail pane */
ConsensusTrendChart {
    height: auto;
    margin: 1 0 0 0;
    padding: 0 1;
    border-top: solid #333300;
    background: #050500;
}

/* Agent Selector */
AgentSelector {
    height: auto;
    min-height: 3;
    background: #001100;
    padding: 0 1;
    margin: 0 0 1 0;
    border: solid #003311;
}

/* Journey View */
JourneyView {
    height: 1fr;
    padding: 0;
    background: #000500;
}

JourneyView .empty-state {
    padding: 2;
    text-align: center;
    color: #666666;
}

JourneyView .content-preview {
    padding: 1;
    background: #001100;
    border: solid #003311;
    margin: 0 0 1 0;
}

/* Journey Phases - color coded by type */
JourneyPhase {
    height: auto;
    margin: 0 0 1 0;
    padding: 0;
}

JourneyPhase.initial {
    border-left: solid #00aaff;
}

JourneyPhase.feedback {
    border-left: solid #ffcc00;
}

JourneyPhase.refinement {
    border-left: solid #cc66ff;
}

JourneyPhase.consensus {
    border-left: solid #00ff41;
}

JourneyPhase .phase-header {
    height: 1;
    padding: 0 1;
    background: #001100;
}

JourneyPhase .phase-header:hover {
    background: #002200;
}

JourneyPhase .phase-content {
    padding: 0 0 0 2;
    height: auto;
}

JourneyPhase.-collapsed .phase-content {
    display: none;
}

/* Feedback Received Card */
FeedbackReceivedCard {
    height: auto;
    margin: 0 0 1 1;
    padding: 0;
}

/* ============================================
   CLARIFICATION MODAL
   Human-centered design with clear feedback
   ============================================ */

#clarification-modal {
    display: none;
    dock: right;
    width: 50%;
    height: 100%;
    background: #000000;
    border-left: thick #00aaff;
}

#clarification-modal.show {
    display: block;
}

ClarificationModal {
    height: 100%;
    background: #000a00;
    padding: 1 2;
}

ClarificationModal.show {
    display: block;
}

ClarificationModal .clarification-header {
    color: #00aaff;
    text-style: bold;
    text-align: center;
    margin-bottom: 1;
}

ClarificationModal .clarification-why {
    color: #666666;
    text-align: center;
}

ClarificationModal .progress-indicator {
    text-align: center;
    margin: 1 0;
}

ClarificationModal #questions-container {
    height: 1fr;
    margin: 1 0;
    background: #000800;
    border: solid #003311;
}

ClarificationModal .question-text {
    color: #00ff88;
    margin-bottom: 1;
}

ClarificationModal .question-option {
    height: 1;
    color: #88cc88;
}

ClarificationModal .question-option.selected {
    color: #00ff41;
}

ClarificationModal .custom-option {
    color: #88aaff;
    margin-bottom: 1;
}

ClarificationModal .custom-input-prompt {
    margin-top: 1;
    color: #00aaff;
}

ClarificationModal #custom-input {
    margin: 0 1 1 1;
    height: 3;
    background: #001500;
    border: solid #00aaff;
    color: #00ff41;
}

ClarificationModal #custom-input.hidden {
    display: none;
}

ClarificationModal .footer-status {
    text-align: center;
    margin: 1 0;
}

ClarificationModal .footer-divider {
    text-align: center;
}

ClarificationModal .clarification-footer {
    color: #888888;
    text-align: center;
}

ClarificationQuestion {
    height: auto;
    margin: 0 0 1 0;
    padding: 1;
    background: #001000;
    border: solid #002200;
}

ClarificationQuestion.focused {
    border: solid #00aaff;
    background: #001515;
}

ClarificationQuestion.focused .question-text {
    color: #00ffff;
}

/* Hotkey styling */
ClarificationModal .hotkey {
    color: #ffaa00;
    text-style: bold;
}
"""
