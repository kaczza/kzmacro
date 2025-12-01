import sys
import time
import json
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QScrollArea, QFrame, QFileDialog, QLineEdit,
    QListWidget, QListWidgetItem, QMessageBox, QSplitter, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from pynput import keyboard, mouse
from PyQt6.QtGui import QFont, QIcon

# -------------------------------------------------------
#               MACRO BLOCK (UI ELEMENT)
# -------------------------------------------------------
class MacroBlock(QFrame):
    def __init__(self, text: str, wait_ms: int, remove_callback):
        super().__init__()
        self.remove_callback = remove_callback
        self.text = text
        self.wait_ms = wait_ms

        self.setStyleSheet("""
            QFrame {
                background-color: #22313f;
                border: 1px solid #0e141a;
                border-radius: 8px;
            }
            QLabel { 
                color: white; 
                font-size: 11px;
                background-color: transparent;
            }
            QPushButton {
                background-color: #9c2b2b;
                color: white;
                border-radius: 7px;
                padding: 0px;
                border: none;
            }
            QPushButton:hover { background-color: #c23737; }
        """)

        self.setFixedSize(105, 40)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)

        self.lbl = QLabel(f"{self.text}\n{self.wait_ms} ms")
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl)
        self.delete = QPushButton("X")
        self.delete.setFixedSize(18, 16)
        self.delete.clicked.connect(self.del_self)
        layout.addWidget(self.delete, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)

    def del_self(self):
        self.remove_callback(self)
        self.deleteLater()

    def export(self):
        return {"text": self.text, "wait": self.wait_ms}


# -------------------------------------------------------
#               KEY LISTENER THREAD
# -------------------------------------------------------
class GlobalKeyListener(QThread):
    key_pressed = pyqtSignal(str)
    
    def __init__(self, assigned_key=None):
        super().__init__()
        self.assigned_key = assigned_key
        self.assigned_mouse_button = None
        self.listener = None
        self.mouse_listener = None
        
    def run(self):
        self.running = True
        
        def on_key_press(key):
            if not self.running:
                return
                
            try:
                k = key.char
            except AttributeError:
                k = str(key)
            
            if self.assigned_key and k == self.assigned_key:
                self.key_pressed.emit(k)
        
        def on_click(x, y, button, pressed):
            if not self.running or not pressed:
                return
            mouse_str = str(button)
            
            if self.assigned_mouse_button and mouse_str == self.assigned_mouse_button:
                self.key_pressed.emit(mouse_str)

        self.listener = keyboard.Listener(on_press=on_key_press)
        self.mouse_listener = mouse.Listener(on_click=on_click)
        
        self.listener.start()
        self.mouse_listener.start()
        while self.running:
            time.sleep(0.1)
        
    def set_assigned_button(self, button_str):
        if button_str.startswith("Button."):
            self.assigned_mouse_button = button_str
            self.assigned_key = None
        else:
            self.assigned_key = button_str
            self.assigned_mouse_button = None
        
    def stop(self):
        self.running = False
        if self.listener:
            self.listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()


# -------------------------------------------------------
#               MACRO PROFILE CLASS
# -------------------------------------------------------
class MacroProfile:
    def __init__(self, name="New Macro"):
        self.name = name
        self.blocks = []  # List of (text, wait_ms)
        self.assigned_button = None
        self.assigned_label = "None"
        
    def add_block(self, text, wait_ms):
        self.blocks.append((text, wait_ms))
        
    def remove_block(self, index):
        if 0 <= index < len(self.blocks):
            self.blocks.pop(index)
            
    def clear_blocks(self):
        self.blocks.clear()
        
    def to_dict(self):
        return {
            "name": self.name,
            "assigned_button": self.assigned_button,
            "assigned_label": self.assigned_label,
            "blocks": [{"text": t, "wait": w} for t, w in self.blocks]
        }
        
    @classmethod
    def from_dict(cls, data):
        profile = cls(data["name"])
        profile.assigned_button = data.get("assigned_button")
        profile.assigned_label = data.get("assigned_label", "None")
        profile.blocks = [(b["text"], b["wait"]) for b in data.get("blocks", [])]
        return profile


# -------------------------------------------------------
#                    MAIN EDITOR
# -------------------------------------------------------
class MacroEditor(QWidget):
    new_key_event = pyqtSignal(str)
    new_mouse_event = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("KzMacro")
        self.resize(1200, 600)

        self.macro_assigned_button = None
        self.current_profile_index = 0
        self.profiles = [MacroProfile("Default Macro")]
        self.recording = False
        self.last_event_time = time.time()
        
        # Global key/mouse listener
        self.global_listener = None
        self.is_listening = False

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("""
            QWidget {
                background-color: #1c252e;
                color: white;
            }
            QListWidget {
                background-color: #151e27;
                border: none;
                color: white;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #22313f;
            }
            QListWidget::item:selected {
                background-color: #2c60ff;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #22313f;
            }
            QPushButton {
                background-color: #33414d;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3d4e5c;
            }
            QPushButton:pressed {
                background-color: #2c3a46;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #22313f;
                color: white;
                border: 1px solid #0e141a;
                border-radius: 4px;
                padding: 4px;
            }
            QInputDialog {
                background-color: #1c252e;
                color: white;
            }
        """)

        # ------------------ LEFT SIDEBAR ------------------
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #151e27;")
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(5, 5, 5, 5)

        # Sidebar title
        sidebar_title = QLabel("Macro Profiles")
        sidebar_title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        sidebar_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(sidebar_title)

        # Profile list
        self.profile_list = QListWidget()
        self.profile_list.setStyleSheet("""
            QListWidget {
                background-color: #151e27;
                border: 1px solid #22313f;
                border-radius: 4px;
            }
        """)
        self.profile_list.addItem("Default Macro")
        self.profile_list.currentRowChanged.connect(self.switch_profile)
        sidebar_layout.addWidget(self.profile_list)

        # Sidebar buttons
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(5)

        self.new_profile_btn = QPushButton("+ New Profile")
        self.new_profile_btn.clicked.connect(self.create_new_profile)
        btn_layout.addWidget(self.new_profile_btn)

        self.rename_profile_btn = QPushButton("Rename")
        self.rename_profile_btn.clicked.connect(self.rename_current_profile)
        btn_layout.addWidget(self.rename_profile_btn)

        self.delete_profile_btn = QPushButton("Delete")
        self.delete_profile_btn.clicked.connect(self.delete_current_profile)
        btn_layout.addWidget(self.delete_profile_btn)

        sidebar_layout.addLayout(btn_layout)
        sidebar_layout.addStretch()
        
        # Save/Load buttons
        save_load_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_profiles)
        save_load_layout.addWidget(self.save_btn)
        
        self.load_btn = QPushButton("Load")
        self.load_btn.clicked.connect(self.load_profiles)
        save_load_layout.addWidget(self.load_btn)
        
        sidebar_layout.addLayout(save_load_layout)
        
        sidebar.setLayout(sidebar_layout)
        main_layout.addWidget(sidebar)

        # ------------------ MAIN CONTENT AREA ------------------
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)

        # ------------------ TOP BUTTONS -------------------
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.record_btn = QPushButton("Record Macro")
        self.record_btn.clicked.connect(self.start_record)
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c60ff;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #3a6fff; }
            QPushButton:disabled { background-color: #1a3f99; }
        """)
        btn_row.addWidget(self.record_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_record)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff2c2c;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #ff3a3a; }
            QPushButton:disabled { background-color: #991a1a; }
        """)
        self.stop_btn.setEnabled(False)
        btn_row.addWidget(self.stop_btn)

        self.assign_btn = QPushButton("Assign to Key/Mouse Button")
        self.assign_btn.clicked.connect(self.assign_button)
        self.assign_btn.setStyleSheet("""
            QPushButton {
                background-color: #2cff88;
                color: #1c252e;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #3aff95; }
        """)
        btn_row.addWidget(self.assign_btn)

        self.profile_name_label = QLabel("Profile: Default Macro")
        self.profile_name_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        btn_row.addWidget(self.profile_name_label)

        self.assigned_lbl = QLabel("Assigned: None")
        self.assigned_lbl.setStyleSheet("font-size: 14px; color: #2cff88;")
        btn_row.addWidget(self.assigned_lbl)

        btn_row.addStretch()
        content_layout.addLayout(btn_row)

        # --------------- SCROLL AREA (TIMELINE) ------------
        timeline_label = QLabel("Macro Timeline")
        timeline_label.setStyleSheet("font-size: 12px; color: #cccccc; margin-top: 10px;")
        content_layout.addWidget(timeline_label)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(280)
        self.scroll.setStyleSheet("""
            QScrollArea {
                background-color: #151e27;
                border: 1px solid #22313f;
                border-radius: 6px;
            }
            QScrollBar:vertical {
                background-color: #22313f;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #2c60ff;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #3a6fff;
            }
        """)

        self.timeline_container = QWidget()
        self.timeline_layout = QHBoxLayout()
        self.timeline_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.timeline_layout.setSpacing(5)
        self.timeline_layout.setContentsMargins(10, 10, 10, 10)
        self.timeline_container.setLayout(self.timeline_layout)

        self.scroll.setWidget(self.timeline_container)
        content_layout.addWidget(self.scroll)

        # ---------------- PLAYBACK CONTROLS ----------------
        playback_layout = QHBoxLayout()
        playback_layout.setSpacing(10)
        
        self.play_btn = QPushButton("▶ Play Macro")
        self.play_btn.clicked.connect(self.play_macro)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: #2cff88;
                color: #1c252e;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #3aff95; }
        """)
        playback_layout.addWidget(self.play_btn)
        
        self.clear_btn = QPushButton("Clear Timeline")
        self.clear_btn.clicked.connect(self.clear_timeline)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff952c;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #ffa33a; }
        """)
        playback_layout.addWidget(self.clear_btn)
        
        playback_layout.addStretch()
        content_layout.addLayout(playback_layout)

        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget, 1)  # Give main content stretch factor

        self.setLayout(main_layout)

        # ---------------- LISTENERS SIGNALS ----------------
        self.new_key_event.connect(self.add_keyblock)
        self.new_mouse_event.connect(self.add_mouseblock)

        self.key_listener = keyboard.Listener(on_press=self.on_key)
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.key_listener.start()
        self.mouse_listener.start()
        self.update_global_listener()

    # -------------------------------------------------------
    #                     PROFILE MANAGEMENT
    # -------------------------------------------------------
    def create_new_profile(self):
        name, ok = QInputDialog.getText(self, "New Profile", "Enter profile name:", text=f"Macro {len(self.profiles) + 1}")
        if ok and name:
            new_profile = MacroProfile(name)
            self.profiles.append(new_profile)
            self.profile_list.addItem(name)
            self.profile_list.setCurrentRow(len(self.profiles) - 1)

    def rename_current_profile(self):
        if not self.profiles:
            return
            
        current_profile = self.profiles[self.current_profile_index]
        name, ok = QInputDialog.getText(self, "Rename Profile", "Enter new name:", text=current_profile.name)
        if ok and name:
            current_profile.name = name
            self.profile_list.item(self.current_profile_index).setText(name)
            self.profile_name_label.setText(f"Profile: {name}")

    def delete_current_profile(self):
        if len(self.profiles) <= 1:
            QMessageBox.warning(self, "Cannot Delete", "You must have at least one profile.")
            return
            
        reply = QMessageBox.question(self, "Delete Profile", 
                                    f"Are you sure you want to delete '{self.profiles[self.current_profile_index].name}'?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.global_listener:
                self.global_listener.stop()
                self.is_listening = False
            self.profiles.pop(self.current_profile_index)
            self.profile_list.takeItem(self.current_profile_index)
            self.current_profile_index = 0
            self.profile_list.setCurrentRow(0)
            self.switch_profile(0)

    def switch_profile(self, index):
        if index < 0 or index >= len(self.profiles):
            return
        self.save_current_profile_state()
        self.current_profile_index = index
        current_profile = self.profiles[index]
        self.profile_name_label.setText(f"Profile: {current_profile.name}")
        if current_profile.assigned_label:
            self.assigned_lbl.setText(f"Assigned: {current_profile.assigned_label}")
        else:
            self.assigned_lbl.setText("Assigned: None")
        self.macro_assigned_button = current_profile.assigned_button
        while self.timeline_layout.count():
            item = self.timeline_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for text, wait_ms in current_profile.blocks:
            blk = MacroBlock(text, wait_ms, self.remove_block)
            self.timeline_layout.addWidget(blk)
        self.update_global_listener()

    def save_current_profile_state(self):
        if not self.profiles:
            return
            
        current_profile = self.profiles[self.current_profile_index]
        current_profile.clear_blocks()
        for i in range(self.timeline_layout.count()):
            blk = self.timeline_layout.itemAt(i).widget()
            if blk:
                current_profile.add_block(blk.text, blk.wait_ms)
        current_profile.assigned_button = self.macro_assigned_button
        current_profile.assigned_label = self.assigned_lbl.text().replace("Assigned: ", "")

    # -------------------------------------------------------
    #                     RECORDING
    # -------------------------------------------------------
    def start_record(self):
        self.recording = True
        self.record_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        while self.timeline_layout.count():
            item = self.timeline_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if self.profiles:
            self.profiles[self.current_profile_index].clear_blocks()

        self.last_event_time = time.time()

    def stop_record(self):
        self.recording = False
        self.record_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def on_key(self, key):
        if not self.recording:
            return

        try:
            k = key.char
        except:
            k = str(key)

        self.new_key_event.emit(k)

    def on_click(self, x, y, button, pressed):
        if not self.recording:
            return

        if pressed:
            self.new_mouse_event.emit(f"{button} Down")
        else:
            self.new_mouse_event.emit(f"{button} Up")

    # -------------------------------------------------------
    #                         ADD BLOCKS
    # -------------------------------------------------------
    def add_keyblock(self, keyname):
        wait = int((time.time() - self.last_event_time) * 1000)
        self.last_event_time = time.time()

        blk = MacroBlock(f"Key {keyname}", wait, self.remove_block)
        self.timeline_layout.addWidget(blk)
        
        # Save to current profile
        if self.profiles:
            self.profiles[self.current_profile_index].add_block(f"Key {keyname}", wait)

    def add_mouseblock(self, txt):
        wait = int((time.time() - self.last_event_time) * 1000)
        self.last_event_time = time.time()

        blk = MacroBlock(txt, wait, self.remove_block)
        self.timeline_layout.addWidget(blk)
        if self.profiles:
            self.profiles[self.current_profile_index].add_block(txt, wait)

    # -------------------------------------------------------
    def remove_block(self, block):
        if self.profiles:
            profile = self.profiles[self.current_profile_index]
            for i, (text, wait) in enumerate(profile.blocks):
                if text == block.text and wait == block.wait_ms:
                    profile.remove_block(i)
                    break
        
        block.setParent(None)
        block.deleteLater()

    def clear_timeline(self):
        while self.timeline_layout.count():
            item = self.timeline_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if self.profiles:
            self.profiles[self.current_profile_index].clear_blocks()

    # -------------------------------------------------------
    #         ASSIGN MACRO TO KEY OR MOUSE BUTTON
    # -------------------------------------------------------
    def assign_button(self):
        self.assigned_lbl.setText("Press any key or mouse button...")
        self.recording = False
        
        # Stop existing listener
        if self.global_listener:
            self.global_listener.stop()
            self.is_listening = False

        def on_key_assign(key):
            try:
                assigned = key.char
            except:
                assigned = str(key)

            self.macro_assigned_button = assigned
            display_name = assigned.replace("Key.", "")
            self.assigned_lbl.setText(f"Assigned: {display_name}")
            if self.profiles:
                self.profiles[self.current_profile_index].assigned_button = assigned
                self.profiles[self.current_profile_index].assigned_label = display_name
            self.update_global_listener()
            
            key_listener.stop()
            mouse_listener.stop()

        def on_mouse_assign(x, y, button, pressed):
            if not pressed:
                return
                
            assigned = str(button)
            self.macro_assigned_button = assigned
            display_name = assigned.replace("Button.", "")
            self.assigned_lbl.setText(f"Assigned: {display_name}")
            if self.profiles:
                self.profiles[self.current_profile_index].assigned_button = assigned
                self.profiles[self.current_profile_index].assigned_label = display_name
            self.update_global_listener()
            
            key_listener.stop()
            mouse_listener.stop()
        key_listener = keyboard.Listener(on_press=on_key_assign)
        mouse_listener = mouse.Listener(on_click=on_mouse_assign)
        
        key_listener.start()
        mouse_listener.start()

    # -------------------------------------------------------
    #           UPDATE GLOBAL LISTENER
    # -------------------------------------------------------
    def update_global_listener(self):
        if self.global_listener:
            self.global_listener.stop()
            self.global_listener.wait(1000)
        current_profile = self.profiles[self.current_profile_index]
        assigned_button = current_profile.assigned_button
        
        if assigned_button:
            self.macro_assigned_button = assigned_button
            self.global_listener = GlobalKeyListener()
            self.global_listener.set_assigned_button(assigned_button)
            self.global_listener.key_pressed.connect(self.on_assigned_button_pressed)
            self.global_listener.start()
            self.is_listening = True
        else:
            self.global_listener = None
            self.is_listening = False

    # -------------------------------------------------------
    #           HANDLE ASSIGNED BUTTON PRESS
    # -------------------------------------------------------
    def on_assigned_button_pressed(self, button_str):
        print(f"Assigned button pressed: {button_str}")
        self.play_macro()

    # -------------------------------------------------------
    #                 MACRO PLAYBACK LOGIC
    # -------------------------------------------------------
    def play_macro(self):
        if not self.profiles or not self.profiles[self.current_profile_index].blocks:
            print("No macro to play")
            return
            
        from pynput.keyboard import Controller, Key
        from pynput.mouse import Controller as MController, Button

        k = Controller()
        m = MController()

        print(f"Playing macro: {self.profiles[self.current_profile_index].name}")
        current_profile = self.profiles[self.current_profile_index]
        for i, (text, wait_ms) in enumerate(current_profile.blocks):
            if i > 0:
                time.sleep(wait_ms / 1000)

            if text.startswith("Key"):
                keyname = text.split(" ")[1]
                try:
                    if hasattr(Key, keyname.lower()):
                        key_obj = getattr(Key, keyname.lower())
                        k.press(key_obj)
                        time.sleep(0.02)
                        k.release(key_obj)
                    else:
                        k.press(keyname)
                        time.sleep(0.02)
                        k.release(keyname)
                except Exception as e:
                    print(f"Error pressing key {keyname}: {e}")

            elif "Button.left" in text:
                if "down" in text:
                    m.press(Button.left)
                elif "up" in text:
                    m.release(Button.left)
                else:
                    m.press(Button.left)
                    time.sleep(0.02)
                    m.release(Button.left)

            elif "Button.right" in text:
                if "down" in text:
                    m.press(Button.right)
                elif "up" in text:
                    m.release(Button.right)
                else:
                    m.press(Button.right)
                    time.sleep(0.02)
                    m.release(Button.right)

            elif "Button.middle" in text:
                if "down" in text:
                    m.press(Button.middle)
                elif "up" in text:
                    m.release(Button.middle)
                else:
                    m.press(Button.middle)
                    time.sleep(0.02)
                    m.release(Button.middle)
                    
            elif "Button.x" in text:
                # Handle mouse buttons X1 and X2 (usually side buttons)
                if "x1" in text.lower():
                    if "down" in text:
                        m.press(Button.x1)
                    elif "up" in text:
                        m.release(Button.x1)
                    else:
                        m.press(Button.x1)
                        time.sleep(0.02)
                        m.release(Button.x1)
                elif "x2" in text.lower():
                    if "down" in text:
                        m.press(Button.x2)
                    elif "up" in text:
                        m.release(Button.x2)
                    else:
                        m.press(Button.x2)
                        time.sleep(0.02)
                        m.release(Button.x2)

    # -------------------------------------------------------
    #                     SAVE/LOAD PROFILES
    # -------------------------------------------------------
    def save_profiles(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Profiles", "", "JSON Files (*.json)"
        )
        
        if file_path:
            if not file_path.endswith('.json'):
                file_path += '.json'
                
            try:
                self.save_current_profile_state()
                
                profiles_data = [profile.to_dict() for profile in self.profiles]
                with open(file_path, 'w') as f:
                    json.dump(profiles_data, f, indent=2)
                QMessageBox.information(self, "Success", "Profiles saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")

    def load_profiles(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Profiles", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    profiles_data = json.load(f)
                self.profiles.clear()
                self.profile_list.clear()
                for data in profiles_data:
                    profile = MacroProfile.from_dict(data)
                    self.profiles.append(profile)
                    self.profile_list.addItem(profile.name)
                if self.profiles:
                    self.profile_list.setCurrentRow(0)
                    self.switch_profile(0)
                    
                QMessageBox.information(self, "Success", "Profiles loaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load: {str(e)}")

    # -------------------------------------------------------
    #                   CLEANUP ON CLOSE
    # -------------------------------------------------------
    def closeEvent(self, event):
        self.save_current_profile_state()
        
        if self.global_listener:
            self.global_listener.stop()
        if self.key_listener:
            self.key_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()
        event.accept()


# -------------------------------------------------------
#                       RUN APP
# -------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        w = MacroEditor()
        w.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()