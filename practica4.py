import pygame
import numpy as np
import random
import math

ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
FPS = 60

pygame.init()
PANTALLA = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Asteroides - Práctica de Transformaciones")
RELOJ = pygame.time.Clock()


class Nave:
    def __init__(self):
       
        self.puntos_locales = np.array([
            [0, -15, 15],  
            [-20, 10, 10], 
            [1, 1, 1]      
        ])
        
        self.posicion = np.array([ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2])
        self.angulo_grados = 0
        self.velocidad = np.array([0.0, 0.0])
        self.radio_colision = 15 
        
    def generar_matriz_rotacion(self, angulo_grados):
        """Crea la matriz de rotación 3x3."""
        theta = np.deg2rad(angulo_grados)
        return np.array([
            [np.cos(theta), -np.sin(theta), 0],
            [np.sin(theta), np.cos(theta), 0],
            [0, 0, 1]
        ])

    def actualizar(self):
        pass

    def rotar(self, giro_grados):
        """Aplica la rotación al ángulo de la nave."""
        self.angulo_grados = (self.angulo_grados + giro_grados) % 360

    def dibujar(self, pantalla):
        """Aplica la transformación (Rotación + Traslación) y dibuja."""
        
        M_rot = self.generar_matriz_rotacion(self.angulo_grados)
        
        puntos_rotados = M_rot @ self.puntos_locales
        
        puntos_globales = (puntos_rotados[:2, :] + self.posicion[:, np.newaxis]).T
        
        pygame.draw.polygon(pantalla, BLANCO, puntos_globales)
        
    def disparar(self, lista_disparos):
       
        punto_punta_local = self.puntos_locales[:, 0]
        
        M_rot = self.generar_matriz_rotacion(self.angulo_grados)
        punto_punta_rotado = M_rot @ punto_punta_local
        
        posicion_disparo = self.posicion + punto_punta_rotado[:2]
        
        velocidad_disparo = -punto_punta_rotado[:2]  
        velocidad_disparo = velocidad_disparo / np.linalg.norm(velocidad_disparo) * 8 

        nuevo_disparo = Disparo(posicion_disparo, -velocidad_disparo * 1.5) 
        lista_disparos.append(nuevo_disparo)


class Asteroide:
    def __init__(self, tamano):
        self.tamano = tamano 
        
        self.radio_colision = tamano * 10 
        
        num_puntos = random.randint(8, 12)
        angulos = np.linspace(0, 2 * np.pi, num_puntos, endpoint=False)
        radios = self.radio_colision + np.random.uniform(-5, 5, num_puntos)
        
        x = radios * np.cos(angulos)
        y = radios * np.sin(angulos)
        self.puntos_locales = np.array([x, y, np.ones(num_puntos)])
        
        lado = random.randint(0, 3)
        if lado == 0: self.posicion = np.array([0.0, float(random.randint(0, ALTO_PANTALLA))]) # Izquierda
        elif lado == 1: self.posicion = np.array([float(ANCHO_PANTALLA), float(random.randint(0, ALTO_PANTALLA))]) # Derecha
        elif lado == 2: self.posicion = np.array([float(random.randint(0, ANCHO_PANTALLA)), 0.0]) # Arriba
        else: self.posicion = np.array([float(random.randint(0, ANCHO_PANTALLA)), float(ALTO_PANTALLA)]) # Abajo
        
        self.velocidad = np.array([random.uniform(-1, 1), random.uniform(-1, 1)])
        
    def actualizar(self):
        self.posicion += self.velocidad
        
        self.posicion[0] = self.posicion[0] % ANCHO_PANTALLA
        self.posicion[1] = self.posicion[1] % ALTO_PANTALLA
        
    def dibujar(self, pantalla):
        """Aplica la Traslación y dibuja."""
        
        puntos_globales = (self.puntos_locales[:2, :] + self.posicion[:, np.newaxis]).T
        
        pygame.draw.polygon(pantalla, BLANCO, puntos_globales, 1) 

class Disparo:
    def __init__(self, posicion, velocidad):
        self.posicion = posicion
        self.velocidad = velocidad
        self.radio = 2
        self.vida = 90 

    def actualizar(self):
        """Aplica la traslación."""
        self.posicion += self.velocidad
        self.vida -= 1

    def dibujar(self, pantalla):
        """Dibuja el disparo (un punto)."""
        pygame.draw.circle(pantalla, BLANCO, (int(self.posicion[0]), int(self.posicion[1])), self.radio)



def verificar_colision(obj1, obj2):
    """Calcula la distancia entre los centros para la colisión circular."""
    dx = obj1.posicion[0] - obj2.posicion[0]
    dy = obj1.posicion[1] - obj2.posicion[1]
    distancia_centros = math.sqrt(dx**2 + dy**2)
    
    return distancia_centros < (obj1.radio_colision + obj2.radio_colision)

def juego_asteroides():
    
    nave = Nave()
    asteroides = []
    disparos = []
    game_over = False
    score = 0
    
    for _ in range(5):
        asteroides.append(Asteroide(tamano=random.randint(2, 3)))
        
    ejecutando = True
    while ejecutando:
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            
            if evento.type == pygame.KEYDOWN and not game_over:
                if evento.key == pygame.K_LEFT:
                    nave.rotar(10) 
                if evento.key == pygame.K_RIGHT:
                    nave.rotar(-10) 
                    
                if evento.key == pygame.K_SPACE:
                    nave.disparar(disparos)
        
        if not game_over:
            
            
            disparos = [d for d in disparos if d.vida > 0] 
            for d in disparos:
                d.actualizar()
                
           
            for a in asteroides:
                a.actualizar()

            
            for d in list(disparos): 
                for a in list(asteroides):
                    d.radio_colision = d.radio 
                    if verificar_colision(d, a):
                        if a.tamano > 1:
                            asteroides.append(Asteroide(a.tamano - 1))
                            asteroides.append(Asteroide(a.tamano - 1))
                        
                        try: asteroides.remove(a)
                        except ValueError: pass 
                        try: disparos.remove(d)
                        except ValueError: pass
                        score += 100
                        break
            
            
            for a in asteroides:
                if verificar_colision(nave, a):
                    game_over = True
                    print(f"¡Juego Terminado! Puntuación Final: {score}")

        
        PANTALLA.fill(NEGRO) 
        
        nave.dibujar(PANTALLA)
        
        for a in asteroides:
            a.dibujar(PANTALLA)
            
        for d in disparos:
            d.dibujar(PANTALLA)
            
        font = pygame.font.Font(None, 36)
        texto = font.render(f"Puntuación: {score}", True, BLANCO)
        PANTALLA.blit(texto, (10, 10))
        
        if game_over:
            font_go = pygame.font.Font(None, 72)
            texto_go = font_go.render("GAME OVER", True, (255, 0, 0))
            PANTALLA.blit(texto_go, (ANCHO_PANTALLA//2 - 150, ALTO_PANTALLA//2 - 36))
            
        pygame.display.flip()
        
        RELOJ.tick(FPS)

    pygame.quit()

if __name__ == '__main__':
    juego_asteroides()