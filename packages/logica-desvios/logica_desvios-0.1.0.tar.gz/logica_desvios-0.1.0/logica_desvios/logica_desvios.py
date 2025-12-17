import threading
import time
import enum
from typing import Callable, Any

class Estado(enum.Enum):
    FECHADO = "fechado"
    ABERTO = "aberto"
    MEIO_ABERTO = "meio_aberto"

class CircuitBreaker:
    """
    Implementa o padrão Circuit Breaker para resiliência em sistemas.
    
    Estados:
    - FECHADO: Permite chamadas, conta falhas.
    - ABERTO: Falha rápido, aguarda timeout para recuperação.
    - MEIO_ABERTO: Testa uma chamada; fecha se sucesso, reabre se falha.
    """
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60, timeout: int = 30):
        """
        Inicializa o Circuit Breaker.
        
        Args:
            failure_threshold: Número de falhas consecutivas para abrir o circuito.
            recovery_timeout: Tempo em segundos para tentar recuperação após abrir.
            timeout: Timeout em segundos para cada chamada.
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.timeout = timeout
        self.state = Estado.FECHADO
        self.failure_count = 0
        self.last_failure_time = None
        self.timer = None
        self.lock = threading.Lock()
        print(f"[DEBUG] CircuitBreaker inicializado: threshold={failure_threshold}, recovery_timeout={recovery_timeout}, timeout={timeout}")
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Executa a função com proteção do Circuit Breaker.
        
        Args:
            func: Função a ser executada.
            *args: Argumentos posicionais para a função.
            **kwargs: Argumentos nomeados para a função.
        
        Returns:
            Resultado da função se sucesso.
        
        Raises:
            Exception: Se o circuito estiver aberto ou a chamada falhar.
        """
        with self.lock:
            if self.state == Estado.ABERTO:
                if self._should_attempt_reset():
                    self.state = Estado.MEIO_ABERTO
                    print("[DEBUG] Circuito em MEIO_ABERTO para teste.")
                else:
                    raise Exception("Circuito aberto: chamada falhada rapidamente.")
            
            if self.state == Estado.MEIO_ABERTO:
                try:
                    result = self._execute_with_timeout(func, *args, **kwargs)
                    self._on_success()
                    return result
                except TimeoutError:
                    # Timeout não conta como falha em MEIO_ABERTO
                    print("[DEBUG] Timeout em MEIO_ABERTO - reabre circuito.")
                    self.state = Estado.ABERTO
                    self._start_recovery_timer()
                    raise
                except Exception as e:
                    self._on_failure()
                    raise e
            
            # Estado FECHADO
            try:
                result = self._execute_with_timeout(func, *args, **kwargs)
                self._on_success()
                return result
            except TimeoutError:
                # Timeout não conta como falha
                print("[DEBUG] Timeout em FECHADO - continua monitorando.")
                raise
            except Exception as e:
                self._on_failure()
                raise e
    
    def is_open(self) -> bool:
        """Verifica se o circuito está aberto."""
        return self.state == Estado.ABERTO
    
    def force_open(self):
        """Força o circuito a abrir manualmente."""
        with self.lock:
            self.state = Estado.ABERTO
            self.failure_count = self.failure_threshold  # Simula falhas
            self.last_failure_time = time.time()
            self._cancel_timer()
            self._start_recovery_timer()
            print("[DEBUG] Circuito forçado a abrir.")
    
    def force_close(self):
        """Força o circuito a fechar manualmente."""
        with self.lock:
            self.state = Estado.FECHADO
            self.failure_count = 0
            self.last_failure_time = None
            self._cancel_timer()
            print("[DEBUG] Circuito forçado a fechar.")
    
    def _execute_with_timeout(self, func: Callable, *args, **kwargs) -> Any:
        """Executa a função com timeout usando threading."""
        result = [None]
        exception = [None]
        
        def target():
            try:
                result[0] = func(*args, **kwargs)
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target)
        thread.start()
        thread.join(self.timeout)
        
        if thread.is_alive():
            raise TimeoutError(f"Chamada excedeu timeout de {self.timeout} segundos.")
        
        if exception[0]:
            raise exception[0]
        
        return result[0]
    
    def _on_success(self):
        """Chamado quando uma chamada é bem-sucedida."""
        self.failure_count = 0
        self.last_failure_time = None
        if self.state == Estado.MEIO_ABERTO:
            self.state = Estado.FECHADO
            self._cancel_timer()
            print("[DEBUG] Circuito fechado após sucesso em MEIO_ABERTO.")
    
    def _on_failure(self):
        """Chamado quando uma chamada falha (não timeout)."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.state == Estado.FECHADO and self.failure_count >= self.failure_threshold:
            self.state = Estado.ABERTO
            self._start_recovery_timer()
            print(f"[DEBUG] Circuito aberto após {self.failure_count} falhas.")
        elif self.state == Estado.MEIO_ABERTO:
            self.state = Estado.ABERTO
            self._start_recovery_timer()
            print("[DEBUG] Circuito reaberto após falha em MEIO_ABERTO.")
    
    def _should_attempt_reset(self) -> bool:
        """Verifica se deve tentar resetar o circuito."""
        if self.last_failure_time is None:
            return False
        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.recovery_timeout
    
    def _start_recovery_timer(self):
        """Inicia timer para recuperação."""
        self._cancel_timer()
        self.timer = threading.Timer(self.recovery_timeout, self._attempt_reset)
        self.timer.start()
        print(f"[DEBUG] Timer de recuperação iniciado por {self.recovery_timeout}s.")
    
    def _attempt_reset(self):
        """Tenta resetar para MEIO_ABERTO."""
        with self.lock:
            if self.state == Estado.ABERTO and self._should_attempt_reset():
                self.state = Estado.MEIO_ABERTO
                print("[DEBUG] Circuito em MEIO_ABERTO após timeout de recuperação.")
    
    def _cancel_timer(self):
        """Cancela o timer ativo."""
        if self.timer:
            self.timer.cancel()
            self.timer = None
            print("[DEBUG] Timer de recuperação cancelado.")
