




import pygame
import sys
import random
import time
import json
import os
from pygame.locals import *

# Initialize pygame
pygame.init()

# Constants
WINDOW_SIZE = 540
GRID_SIZE = 9
CELL_SIZE = WINDOW_SIZE // GRID_SIZE
FONT_SIZE = 36
SMALL_FONT_SIZE = 18
BUTTON_FONT_SIZE = 16

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (70, 130, 180)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
LIGHT_RED = (255, 200, 200)
LIGHT_GREEN = (144, 238, 144)
BACKGROUND = (245, 245, 245)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Difficulty settings - number of given cells
DIFFICULTY_LEVELS = {
    "آسان": 45,      # 45 given numbers
    "متوسط": 35,     # 35 given numbers  
    "سخت": 28,       # 28 given numbers
    "بسیار سخت": 22  # 22 given numbers
}

class SudokuGenerator:
    def __init__(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = [[0 for _ in range(9)] for _ in range(9)]
    
    def generate_board(self, difficulty_level="متوسط"):
        """Generate a new Sudoku board with given difficulty level"""
        given_numbers = DIFFICULTY_LEVELS[difficulty_level]
        empty_cells = 81 - given_numbers
        
        # Fill diagonal 3x3 boxes
        self._fill_diagonal()
        # Solve the complete board
        self._solve_sudoku()
        # Save the solution
        self.solution = [row[:] for row in self.board]
        # Remove numbers to create puzzle
        self._remove_numbers(empty_cells)
        return self.board, self.solution
    
    def _fill_diagonal(self):
        for i in range(0, 9, 3):
            numbers = list(range(1, 10))
            random.shuffle(numbers)
            for j in range(3):
                for k in range(3):
                    self.board[i+j][i+k] = numbers.pop()
    
    def _solve_sudoku(self):
        find = self._find_empty()
        if not find:
            return True
        row, col = find
        
        for num in range(1, 10):
            if self._is_valid(row, col, num):
                self.board[row][col] = num
                if self._solve_sudoku():
                    return True
                self.board[row][col] = 0
        return False
    
    def _find_empty(self):
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    return (i, j)
        return None
    
    def _is_valid(self, row, col, num):
        # Check row
        for j in range(9):
            if self.board[row][j] == num:
                return False
        
        # Check column
        for i in range(9):
            if self.board[i][col] == num:
                return False
        
        # Check 3x3 box
        box_x = col // 3
        box_y = row // 3
        for i in range(box_y*3, box_y*3 + 3):
            for j in range(box_x*3, box_x*3 + 3):
                if self.board[i][j] == num and (i, j) != (row, col):
                    return False
        
        return True
    
    def _remove_numbers(self, empty_cells_count):
        """Remove numbers from the solved board to create the puzzle"""
        cells = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(cells)
        
        removed = 0
        for row, col in cells:
            if removed >= empty_cells_count:
                break
            if self.board[row][col] != 0:
                # Store the value
                temp = self.board[row][col]
                self.board[row][col] = 0
                
                # Check if the puzzle still has unique solution
                temp_board = [row[:] for row in self.board]
                solutions = self._count_solutions()
                if solutions == 1:
                    removed += 1
                else:
                    self.board[row][col] = temp
    
    def _count_solutions(self):
        """Count number of solutions (simplified version)"""
        # For performance, we'll use a simplified check
        # In a full implementation, you'd use a more robust method
        temp_board = [row[:] for row in self.board]
        count = self._solve_and_count()
        self.board = [row[:] for row in temp_board]
        return count
    
    def _solve_and_count(self, count=0):
        find = self._find_empty()
        if not find:
            return count + 1
        
        row, col = find
        for num in range(1, 10):
            if self._is_valid(row, col, num):
                self.board[row][col] = num
                count = self._solve_and_count(count)
                self.board[row][col] = 0
                if count > 1:  # Early exit if multiple solutions found
                    break
        return count

class GameData:
    def __init__(self):
        self.filename = "sudoku_records.json"
        self.records = self.load_records()
    
    def load_records(self):
        """Load game records from JSON file"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        
        # Default structure if file doesn't exist
        return {
            "آسان": {"best_time": None, "history": []},
            "متوسط": {"best_time": None, "history": []},
            "سخت": {"best_time": None, "history": []},
            "بسیار سخت": {"best_time": None, "history": []}
        }
    
    def save_records(self):
        """Save game records to JSON file"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def add_record(self, difficulty, time_taken):
        """Add a new record for the given difficulty"""
        record = {
            "time": time_taken,
            "date": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.records[difficulty]["history"].append(record)
        
        # Update best time
        if (self.records[difficulty]["best_time"] is None or 
            time_taken < self.records[difficulty]["best_time"]):
            self.records[difficulty]["best_time"] = time_taken
            self.save_records()
            return True  # New record!
        
        self.save_records()
        return False  # Not a new record
    
    def get_best_time(self, difficulty):
        """Get best time for given difficulty"""
        return self.records[difficulty]["best_time"]
    
    def get_average_time(self, difficulty):
        """Calculate average time for given difficulty"""
        history = self.records[difficulty]["history"]
        if not history:
            return None
        total = sum(record["time"] for record in history)
        return total / len(history)

class SudokuGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 150))
        pygame.display.set_caption('سودوکو حرفه‌ای - Professional Sudoku')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', FONT_SIZE)
        self.small_font = pygame.font.SysFont('Arial', SMALL_FONT_SIZE)
        self.button_font = pygame.font.SysFont('Arial', BUTTON_FONT_SIZE)
        
        self.generator = SudokuGenerator()
        self.game_data = GameData()
        
        # Game state
        self.difficulty = "متوسط"
        self.board, self.solution = self.generator.generate_board(self.difficulty)
        self.original_board = [row[:] for row in self.board]
        
        self.selected = None
        self.errors = 0
        self.start_time = time.time()
        self.current_time = 0
        self.game_over = False
        self.checked_cells = set()  # Cells that have been checked
        self.showing_check = False  # Whether we're currently showing check results
        
        # Load images or create surfaces for UI elements
        self._create_ui_elements()
    
    def _create_ui_elements(self):
        """Create UI elements like buttons"""
        # Difficulty buttons
        self.diff_buttons = {}
        x_pos = 20
        for diff in DIFFICULTY_LEVELS.keys():
            self.diff_buttons[diff] = pygame.Rect(x_pos, WINDOW_SIZE + 10, 100, 30)
            x_pos += 110
        
        # Control buttons
        self.new_game_button = pygame.Rect(20, WINDOW_SIZE + 50, 100, 35)
        self.check_button = pygame.Rect(140, WINDOW_SIZE + 50, 100, 35)
        self.solve_button = pygame.Rect(260, WINDOW_SIZE + 50, 100, 35)
        self.hint_button = pygame.Rect(380, WINDOW_SIZE + 50, 100, 35)
    
    def draw_grid(self):
        """Draw the Sudoku grid"""
        self.screen.fill(BACKGROUND)
        
        # Draw the main grid
        for i in range(GRID_SIZE + 1):
            # Thicker lines for 3x3 boxes
            line_width = 4 if i % 3 == 0 else 1
            
            # Horizontal lines
            pygame.draw.line(
                self.screen, BLACK, 
                (0, i * CELL_SIZE), 
                (WINDOW_SIZE, i * CELL_SIZE), 
                line_width
            )
            # Vertical lines
            pygame.draw.line(
                self.screen, BLACK, 
                (i * CELL_SIZE, 0), 
                (i * CELL_SIZE, WINDOW_SIZE), 
                line_width
            )
        
        # Highlight selected cell
        if self.selected:
            row, col = self.selected
            pygame.draw.rect(
                self.screen, LIGHT_BLUE,
                (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            )
        
        # Highlight checked cells (correct/incorrect)
        if self.showing_check:
            for row, col in self.checked_cells:
                if self.board[row][col] != 0:
                    if self.board[row][col] == self.solution[row][col]:
                        # Correct - light green
                        pygame.draw.rect(
                            self.screen, LIGHT_GREEN,
                            (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        )
                    else:
                        # Incorrect - light red
                        pygame.draw.rect(
                            self.screen, LIGHT_RED,
                            (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        )
    
    def draw_numbers(self):
        """Draw numbers on the grid"""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.board[row][col] != 0:
                    # Determine color based on cell state
                    if self.original_board[row][col] != 0:
                        color = BLACK  # Original numbers
                    elif self.showing_check and (row, col) in self.checked_cells:
                        if self.board[row][col] == self.solution[row][col]:
                            color = GREEN  # Correct user input
                        else:
                            color = RED  # Incorrect user input
                    else:
                        color = DARK_BLUE  # Regular user input
                    
                    number_text = self.font.render(str(self.board[row][col]), True, color)
                    text_rect = number_text.get_rect(
                        center=((col * CELL_SIZE) + CELL_SIZE // 2, 
                               (row * CELL_SIZE) + CELL_SIZE // 2)
                    )
                    self.screen.blit(number_text, text_rect)
    
    def draw_ui(self):
        """Draw the user interface elements"""
        # Draw difficulty buttons
        for diff, rect in self.diff_buttons.items():
            color = LIGHT_GREEN if diff == self.difficulty else LIGHT_BLUE
            pygame.draw.rect(self.screen, color, rect)
            diff_text = self.button_font.render(diff, True, BLACK)
            text_rect = diff_text.get_rect(center=rect.center)
            self.screen.blit(diff_text, text_rect)
        
        # Draw control buttons
        pygame.draw.rect(self.screen, LIGHT_GREEN, self.new_game_button)
        pygame.draw.rect(self.screen, YELLOW, self.check_button)
        pygame.draw.rect(self.screen, LIGHT_BLUE, self.solve_button)
        pygame.draw.rect(self.screen, PURPLE, self.hint_button)
        
        # Draw button text
        new_game_text = self.button_font.render("بازی جدید", True, BLACK)
        check_text = self.button_font.render("بررسی پاسخ", True, BLACK)
        solve_text = self.button_font.render("حل سودوکو", True, BLACK)
        hint_text = self.button_font.render("راهنمایی", True, BLACK)
        
        self.screen.blit(new_game_text, (self.new_game_button.x + 20, self.new_game_button.y + 10))
        self.screen.blit(check_text, (self.check_button.x + 20, self.check_button.y + 10))
        self.screen.blit(solve_text, (self.solve_button.x + 20, self.solve_button.y + 10))
        self.screen.blit(hint_text, (self.hint_button.x + 20, self.hint_button.y + 10))
        
        # Draw game info
        self.current_time = int(time.time() - self.start_time)
        
        errors_text = self.small_font.render(f"تعداد خطا: {self.errors}", True, BLACK)
        time_text = self.small_font.render(f"زمان: {self.format_time(self.current_time)}", True, BLACK)
        difficulty_text = self.small_font.render(f"سطح: {self.difficulty}", True, BLACK)
        
        best_time = self.game_data.get_best_time(self.difficulty)
        best_text = self.small_font.render(
            f"بهترین زمان: {self.format_time(best_time) if best_time else '---'}", 
            True, BLACK
        )
        
        self.screen.blit(errors_text, (20, WINDOW_SIZE + 95))
        self.screen.blit(time_text, (150, WINDOW_SIZE + 95))
        self.screen.blit(difficulty_text, (280, WINDOW_SIZE + 95))
        self.screen.blit(best_text, (380, WINDOW_SIZE + 95))
        
        # Game over message
        if self.game_over:
            game_over_text = self.font.render("تبریک! سودوکو حل شد! 🎉", True, GREEN)
            text_rect = game_over_text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2))
            
            # Draw background for message
            pygame.draw.rect(self.screen, WHITE, text_rect.inflate(40, 20))
            pygame.draw.rect(self.screen, GREEN, text_rect.inflate(40, 20), 3)
            
            self.screen.blit(game_over_text, text_rect)
            
            # Show record message if applicable
            best_time = self.game_data.get_best_time(self.difficulty)
            if best_time == self.current_time:
                record_text = self.small_font.render("🎊 رکورد جدید! 🎊", True, PURPLE)
                record_rect = record_text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2 + 40))
                self.screen.blit(record_text, record_rect)
    
    def format_time(self, seconds):
        """Format seconds into MM:SS format"""
        if seconds is None:
            return "--:--"
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def handle_click(self, pos):
        """Handle mouse clicks"""
        x, y = pos
        
        # Check if click is within the grid
        if y < WINDOW_SIZE:
            row = y // CELL_SIZE
            col = x // CELL_SIZE
            self.selected = (row, col)
            return
        
        # Check difficulty buttons
        for diff, rect in self.diff_buttons.items():
            if rect.collidepoint(pos) and diff != self.difficulty:
                self.change_difficulty(diff)
                return
        
        # Check control buttons
        if self.new_game_button.collidepoint(pos):
            self.new_game()
        elif self.check_button.collidepoint(pos):
            self.check_solution()
        elif self.solve_button.collidepoint(pos):
            self.solve_board()
        elif self.hint_button.collidepoint(pos):
            self.give_hint()
    
    def handle_keypress(self, key):
        """Handle keyboard input"""
        if not self.selected or self.game_over:
            return
        
        row, col = self.selected
        
        # Only allow input in non-original cells
        if self.original_board[row][col] == 0:
            if pygame.K_1 <= key <= pygame.K_9:
                number = key - pygame.K_0
                old_value = self.board[row][col]
                self.board[row][col] = number
                
                # Check if the move is correct
                if number != self.solution[row][col]:
                    self.errors += 1
                
                self.check_win()
            
            elif key == pygame.K_BACKSPACE or key == pygame.K_DELETE or key == pygame.K_0:
                self.board[row][col] = 0
            
            # Move selection with arrow keys
            elif key == pygame.K_UP and row > 0:
                self.selected = (row - 1, col)
            elif key == pygame.K_DOWN and row < 8:
                self.selected = (row + 1, col)
            elif key == pygame.K_LEFT and col > 0:
                self.selected = (row, col - 1)
            elif key == pygame.K_RIGHT and col < 8:
                self.selected = (row, col + 1)
    
    def change_difficulty(self, new_difficulty):
        """Change game difficulty"""
        self.difficulty = new_difficulty
        self.new_game()
    
    def new_game(self):
        """Start a new game"""
        self.board, self.solution = self.generator.generate_board(self.difficulty)
        self.original_board = [row[:] for row in self.board]
        self.selected = None
        self.errors = 0
        self.start_time = time.time()
        self.current_time = 0
        self.game_over = False
        self.checked_cells.clear()
        self.showing_check = False
    
    def check_solution(self):
        """Check the current solution and highlight correct/incorrect cells"""
        self.checked_cells.clear()
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if (self.original_board[row][col] == 0 and 
                    self.board[row][col] != 0):
                    self.checked_cells.add((row, col))
        
        self.showing_check = True
    
    def solve_board(self):
        """Solve the entire board"""
        self.board = [row[:] for row in self.solution]
        self.game_over = True
        self._finish_game()
    
    def give_hint(self):
        """Give a hint by filling one correct cell"""
        if self.game_over:
            return
        
        # Find an empty cell
        empty_cells = []
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.board[row][col] == 0:
                    empty_cells.append((row, col))
        
        if empty_cells:
            # Pick a random empty cell
            row, col = random.choice(empty_cells)
            self.board[row][col] = self.solution[row][col]
            self.selected = (row, col)
            
            # Check if game is won after hint
            self.check_win()
    
    def check_win(self):
        """Check if the player has won"""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.board[row][col] != self.solution[row][col]:
                    return False
        
        self.game_over = True
        self._finish_game()
        return True
    
    def _finish_game(self):
        """Handle game completion"""
        if self.game_over:
            # Add record and check if it's a new best
            is_new_record = self.game_data.add_record(self.difficulty, self.current_time)
            
            if is_new_record:
                print(f"🎉 رکورد جدید در سطح {self.difficulty}! زمان: {self.format_time(self.current_time)}")
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == KEYDOWN:
                    self.handle_keypress(event.key)
            
            self.draw_grid()
            self.draw_numbers()
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SudokuGame()
    game.run()