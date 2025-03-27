# YakTaa - Interface utilisateur de combat
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Any, Optional, Callable
from .engine import CombatEngine, ActionType, CombatStatus

# Configurer le logger
logger = logging.getLogger(__name__)

class CombatUI:
    """Interface utilisateur pour les combats"""
    
    def __init__(self, root, combat_engine: CombatEngine, end_callback: Callable = None):
        """Initialise l'interface utilisateur de combat
        
        Args:
            root: Fenêtre racine Tkinter
            combat_engine: Moteur de combat à utiliser
            end_callback: Fonction à appeler à la fin du combat
        """
        self.root = root
        self.combat_engine = combat_engine
        self.end_callback = end_callback
        
        # Création de la fenêtre de combat
        self.combat_frame = ttk.Frame(root)
        self.combat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Création des différentes sections
        self._create_info_section()
        self._create_log_section()
        self._create_action_section()
        self._create_target_selection()
        
        # Style cyberpunk
        self._apply_cyberpunk_style()
        
        # Démarrer le combat
        self.combat_engine.start_combat()
        self._update_ui()
        
    def _create_info_section(self):
        """Crée la section d'information sur le combat (santé, statut)"""
        info_frame = ttk.LabelFrame(self.combat_frame, text="Statut du combat")
        info_frame.pack(fill=tk.X, pady=5)
        
        # Info sur le joueur
        player_frame = ttk.Frame(info_frame)
        player_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(player_frame, text="Joueur:").grid(row=0, column=0, sticky=tk.W)
        self.player_name_label = ttk.Label(player_frame, text=self.combat_engine.player.name)
        self.player_name_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(player_frame, text="Santé:").grid(row=1, column=0, sticky=tk.W)
        self.player_health_bar = ttk.Progressbar(player_frame, length=150, mode='determinate')
        self.player_health_bar.grid(row=1, column=1, padx=5, pady=2)
        self.player_health_text = ttk.Label(player_frame, text="0/0")
        self.player_health_text.grid(row=1, column=2, sticky=tk.W)
        
        ttk.Label(player_frame, text="Effets actifs:").grid(row=2, column=0, sticky=tk.W)
        self.player_effects_label = ttk.Label(player_frame, text="Aucun")
        self.player_effects_label.grid(row=2, column=1, columnspan=2, sticky=tk.W)
        
        # Info sur les ennemis
        enemies_frame = ttk.LabelFrame(info_frame, text="Ennemis")
        enemies_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.enemy_frames = []
        for i, enemy in enumerate(self.combat_engine.enemies):
            enemy_frame = ttk.Frame(enemies_frame)
            enemy_frame.pack(fill=tk.X, padx=2, pady=2)
            
            enemy_name_label = ttk.Label(enemy_frame, text=enemy.name)
            enemy_name_label.grid(row=0, column=0, sticky=tk.W)
            
            enemy_health_bar = ttk.Progressbar(enemy_frame, length=100, mode='determinate')
            enemy_health_bar.grid(row=0, column=1, padx=5)
            
            enemy_health_text = ttk.Label(enemy_frame, text="0/0")
            enemy_health_text.grid(row=0, column=2, sticky=tk.W)
            
            enemy_effects_label = ttk.Label(enemy_frame, text="")
            enemy_effects_label.grid(row=1, column=0, columnspan=3, sticky=tk.W)
            
            self.enemy_frames.append({
                "name": enemy_name_label,
                "health_bar": enemy_health_bar,
                "health_text": enemy_health_text,
                "effects": enemy_effects_label,
                "enemy": enemy
            })
        
        # Info sur le tour actuel
        turn_frame = ttk.Frame(info_frame)
        turn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(turn_frame, text="Tour:").grid(row=0, column=0, sticky=tk.W)
        self.turn_label = ttk.Label(turn_frame, text="1")
        self.turn_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(turn_frame, text="Tour de:").grid(row=1, column=0, sticky=tk.W)
        self.current_actor_label = ttk.Label(turn_frame, text="")
        self.current_actor_label.grid(row=1, column=1, sticky=tk.W)
    
    def _create_log_section(self):
        """Crée la section de logs du combat"""
        log_frame = ttk.LabelFrame(self.combat_frame, text="Journal de combat")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD, bg='#0a0a0a', fg='#00ffcc')
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.config(state=tk.DISABLED)
    
    def _create_action_section(self):
        """Crée la section des actions de combat"""
        action_frame = ttk.LabelFrame(self.combat_frame, text="Actions")
        action_frame.pack(fill=tk.X, pady=5)
        
        # Créer les boutons d'action
        buttons_frame = ttk.Frame(action_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.attack_btn = ttk.Button(
            buttons_frame, 
            text="Attaquer", 
            command=lambda: self._on_action_selected(ActionType.ATTACK)
        )
        self.attack_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.hack_btn = ttk.Button(
            buttons_frame, 
            text="Hacker", 
            command=lambda: self._on_action_selected(ActionType.HACK)
        )
        self.hack_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.use_item_btn = ttk.Button(
            buttons_frame, 
            text="Utiliser Objet", 
            command=lambda: self._on_action_selected(ActionType.USE_ITEM)
        )
        self.use_item_btn.grid(row=0, column=2, padx=5, pady=5)
        
        self.activate_implant_btn = ttk.Button(
            buttons_frame, 
            text="Activer Implant", 
            command=lambda: self._on_action_selected(ActionType.ACTIVATE_IMPLANT)
        )
        self.activate_implant_btn.grid(row=0, column=3, padx=5, pady=5)
        
        self.defend_btn = ttk.Button(
            buttons_frame, 
            text="Défendre", 
            command=lambda: self._execute_action(ActionType.DEFEND)
        )
        self.defend_btn.grid(row=1, column=0, padx=5, pady=5)
        
        self.scan_btn = ttk.Button(
            buttons_frame, 
            text="Scanner", 
            command=lambda: self._on_action_selected(ActionType.SCAN)
        )
        self.scan_btn.grid(row=1, column=1, padx=5, pady=5)
        
        self.escape_btn = ttk.Button(
            buttons_frame, 
            text="Fuir", 
            command=lambda: self._execute_action(ActionType.ESCAPE)
        )
        self.escape_btn.grid(row=1, column=2, padx=5, pady=5)
    
    def _create_target_selection(self):
        """Crée la section de sélection de cible"""
        self.target_frame = ttk.LabelFrame(self.combat_frame, text="Sélection de cible")
        
        # Cette section est masquée par défaut, elle sera affichée seulement
        # lorsqu'une action nécessitant une cible est sélectionnée
        
        # Créer la liste de sélection des cibles
        self.target_var = tk.StringVar()
        self.target_listbox = tk.Listbox(self.target_frame, listvariable=self.target_var, height=5)
        self.target_listbox.pack(fill=tk.X, padx=5, pady=5)
        
        # Boutons de confirmation/annulation
        btn_frame = ttk.Frame(self.target_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.confirm_btn = ttk.Button(btn_frame, text="Confirmer", command=self._on_target_confirmed)
        self.confirm_btn.pack(side=tk.LEFT, padx=5)
        
        self.cancel_btn = ttk.Button(btn_frame, text="Annuler", command=self._on_target_cancelled)
        self.cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Variables d'état pour la sélection d'action/cible
        self.current_action = None
        self.current_item = None
    
    def _apply_cyberpunk_style(self):
        """Applique un style cyberpunk à l'interface"""
        # Définir un style personnalisé
        style = ttk.Style()
        
        # Style de la fenêtre principale
        self.root.configure(bg='#0a0a0a')
        style.configure('TFrame', background='#1a1a1a')
        style.configure('TLabelframe', background='#1a1a1a', foreground='#00ffcc')
        style.configure('TLabelframe.Label', background='#1a1a1a', foreground='#00ffcc')
        
        # Style des widgets
        style.configure('TLabel', background='#1a1a1a', foreground='#00ffcc')
        style.configure('TButton', background='#2a2a2a', foreground='#00ffcc', 
                      font=('Arial', 9, 'bold'))
        
        # Style des barres de progression
        style.configure("TProgressbar", background='#00ffcc', troughcolor='#2a2a2a')
    
    def _update_ui(self):
        """Met à jour l'interface utilisateur avec l'état actuel du combat"""
        # Mettre à jour les informations sur le joueur
        player = self.combat_engine.player
        max_health = getattr(player, 'max_health', 100)
        
        # Mettre à jour la barre de santé du joueur
        health_percent = (player.health / max_health) * 100
        self.player_health_bar['value'] = health_percent
        self.player_health_text['text'] = f"{player.health}/{max_health}"
        
        # Mettre à jour les effets actifs du joueur
        player_effects = self.combat_engine.active_effects.get(player, [])
        if player_effects:
            self.player_effects_label['text'] = ", ".join(player_effects)
        else:
            self.player_effects_label['text'] = "Aucun"
        
        # Mettre à jour les informations sur les ennemis
        for i, enemy_frame in enumerate(self.enemy_frames):
            enemy = enemy_frame["enemy"]
            max_enemy_health = getattr(enemy, 'max_health', 100)
            
            # Mettre à jour la barre de santé de l'ennemi
            enemy_health_percent = (enemy.health / max_enemy_health) * 100
            enemy_frame["health_bar"]['value'] = enemy_health_percent
            enemy_frame["health_text"]['text'] = f"{enemy.health}/{max_enemy_health}"
            
            # Mettre à jour les effets actifs de l'ennemi
            enemy_effects = self.combat_engine.active_effects.get(enemy, [])
            if enemy_effects:
                enemy_frame["effects"]['text'] = "Effets: " + ", ".join(enemy_effects)
            else:
                enemy_frame["effects"]['text'] = ""
        
        # Mettre à jour les informations sur le tour
        self.turn_label['text'] = str(self.combat_engine.current_turn)
        self.current_actor_label['text'] = self.combat_engine.current_actor.name
        
        # Activer/désactiver les boutons d'action en fonction du joueur actuel
        is_player_turn = self.combat_engine.current_actor == self.combat_engine.player
        state = tk.NORMAL if is_player_turn else tk.DISABLED
        
        for btn in [self.attack_btn, self.hack_btn, self.use_item_btn, 
                   self.activate_implant_btn, self.defend_btn, 
                   self.scan_btn, self.escape_btn]:
            btn['state'] = state
        
        # Mettre à jour le journal de combat
        self._update_combat_log()
        
        # Vérifier si le combat est terminé
        if self.combat_engine.status != CombatStatus.IN_PROGRESS:
            self._handle_combat_end()
    
    def _update_combat_log(self):
        """Met à jour le journal de combat avec les derniers messages"""
        # Activer l'édition du texte
        self.log_text.config(state=tk.NORMAL)
        
        # Effacer le contenu actuel
        self.log_text.delete(1.0, tk.END)
        
        # Ajouter tous les messages de log
        for message in self.combat_engine.log_messages:
            self.log_text.insert(tk.END, message + "\n")
        
        # Faire défiler jusqu'au bas
        self.log_text.see(tk.END)
        
        # Désactiver l'édition du texte
        self.log_text.config(state=tk.DISABLED)
    
    def _on_action_selected(self, action_type: ActionType):
        """Gère la sélection d'une action par le joueur"""
        self.current_action = action_type
        
        # Certaines actions nécessitent une cible
        if action_type in [ActionType.ATTACK, ActionType.HACK, ActionType.SCAN]:
            self._show_target_selection()
        elif action_type in [ActionType.USE_ITEM, ActionType.ACTIVATE_IMPLANT]:
            # TODO: Implémenter la sélection d'objet/implant
            messagebox.showinfo("Non implémenté", "Cette fonctionnalité n'est pas encore implémentée")
            self.current_action = None
        else:
            # Actions qui ne nécessitent pas de cible (défendre, fuir)
            self._execute_action(action_type)
    
    def _show_target_selection(self):
        """Affiche l'interface de sélection de cible"""
        # Mette à jour la liste des cibles disponibles
        targets = [enemy.name for enemy in self.combat_engine.enemies if enemy.health > 0]
        self.target_var.set(tuple(targets))
        
        # Afficher le cadre de sélection de cible
        self.target_frame.pack(fill=tk.X, pady=5)
    
    def _on_target_confirmed(self):
        """Gère la confirmation de la sélection d'une cible"""
        # Vérifier qu'une cible est sélectionnée
        selection = self.target_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aucune cible", "Veuillez sélectionner une cible")
            return
        
        # Récupérer la cible sélectionnée
        target_index = selection[0]
        if target_index < 0 or target_index >= len(self.combat_engine.enemies):
            return
        
        target = self.combat_engine.enemies[target_index]
        
        # Exécuter l'action avec la cible sélectionnée
        self._execute_action(self.current_action, target)
        
        # Masquer le cadre de sélection de cible
        self.target_frame.pack_forget()
    
    def _on_target_cancelled(self):
        """Gère l'annulation de la sélection de cible"""
        self.current_action = None
        self.target_frame.pack_forget()
    
    def _execute_action(self, action_type: ActionType, target=None, item=None):
        """Exécute une action de combat"""
        # Exécuter l'action via le moteur de combat
        result = self.combat_engine.perform_action(action_type, target, item)
        
        # Si l'action a réussi, mettre à jour l'interface
        if result.get("success", False):
            self._update_ui()
            
            # Si ce n'est plus le tour du joueur, simuler le tour des ennemis
            if self.combat_engine.current_actor != self.combat_engine.player:
                self.root.after(1000, self._handle_enemy_turn)
        else:
            # Afficher un message d'erreur si l'action a échoué
            messagebox.showwarning("Action échouée", result.get("message", "L'action a échoué"))
    
    def _handle_enemy_turn(self):
        """Gère automatiquement le tour des ennemis"""
        if self.combat_engine.status != CombatStatus.IN_PROGRESS:
            return
            
        # Pour cet exemple, les ennemis font simplement une action par défaut
        # Dans une implémentation complète, ils auraient une IA plus élaborée
        
        # Simuler une pause pour l'animation
        self.root.after(500, self._simulate_enemy_action)
    
    def _simulate_enemy_action(self):
        """Simule une action pour l'ennemi actuel"""
        if self.combat_engine.status != CombatStatus.IN_PROGRESS:
            return
            
        current_actor = self.combat_engine.current_actor
        
        # L'ennemi attaque toujours le joueur dans cet exemple
        # Une IA plus complexe prendrait des décisions basées sur l'état du combat
        
        # Simuler une attaque
        damage = getattr(current_actor, 'damage', 10)
        resistance = getattr(self.combat_engine.player, 'resistance_physical', 0)
        damage_multiplier = 1.0 - (resistance / 100)
        final_damage = max(1, int(damage * damage_multiplier))
        
        # Appliquer les dégâts au joueur
        self.combat_engine.player.health -= final_damage
        
        # Enregistrer l'action dans le journal
        message = f"{current_actor.name} attaque {self.combat_engine.player.name} et inflige {final_damage} dégâts"
        self.combat_engine.log_message(message)
        
        # Passer au joueur suivant
        next_turn_result = self.combat_engine.next_turn()
        
        # Mettre à jour l'interface
        self._update_ui()
        
        # Si c'est encore le tour d'un ennemi, continuer la simulation
        if self.combat_engine.current_actor != self.combat_engine.player and self.combat_engine.status == CombatStatus.IN_PROGRESS:
            self.root.after(1000, self._handle_enemy_turn)
    
    def _handle_combat_end(self):
        """Gère la fin du combat"""
        # Désactiver tous les boutons d'action
        for btn in [self.attack_btn, self.hack_btn, self.use_item_btn, 
                   self.activate_implant_btn, self.defend_btn, 
                   self.scan_btn, self.escape_btn]:
            btn['state'] = tk.DISABLED
        
        # Afficher un message de fin de combat
        if self.combat_engine.status == CombatStatus.PLAYER_VICTORY:
            message = "Victoire ! Vous avez vaincu tous les ennemis."
            title = "Victoire"
        elif self.combat_engine.status == CombatStatus.ENEMY_VICTORY:
            message = "Défaite ! Vous avez été vaincu."
            title = "Défaite"
        elif self.combat_engine.status == CombatStatus.ESCAPED:
            message = "Vous avez réussi à fuir le combat."
            title = "Fuite"
        else:
            message = "Le combat est terminé."
            title = "Fin du combat"
        
        # Afficher le message et appeler le callback de fin si défini
        messagebox.showinfo(title, message)
        
        if self.end_callback:
            self.end_callback(self.combat_engine.status)
