import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class ToolAIWidget(ttk.Frame):
    def __init__(self, master, ai_service):
        ttk.Frame.__init__(self, master)
        super().__init__(master)
        self.master = master
        self.ai_service = ai_service
        self.create_widget()

    def create_widget(self) -> None:
        self.ai_frame = ttk.Frame(self, style="frame.TFrame")
        self.ai_frame.pack(fill=BOTH, expand=True)

        self.ai_label = ttk.Label(
            self.ai_frame, text="AI模型", style="tool.TLabel"
        )
        self.ai_label.pack(side=TOP, padx=5, pady=(5, 0))

        self.model_var = ttk.StringVar()
        self.model_combobox = ttk.Combobox(
            self.ai_frame,
            textvariable=self.model_var,
            values=self.ai_service.get_available_models(),
            state="readonly",
            width=22,
            font=("等线", 10),
        )
        self.model_combobox.pack(side=TOP, padx=5, pady=(0, 5))

        if self.ai_service.current_model:
            self.model_var.set(self.ai_service.current_model)

        self.model_combobox.bind("<<ComboboxSelected>>", self._on_model_selected)

    def _on_model_selected(self, event) -> None:
        selected = self.model_var.get()
        if selected:
            self.ai_service.set_model(selected)

    def get_current_model(self) -> str:
        return self.model_var.get()
