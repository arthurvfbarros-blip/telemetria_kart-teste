#include <iostream>
#include <string>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <termios.h>

// Função para ler teclado sem precisar de "Enter" (padrão Linux)
char getch() {
    char buf = 0;
    struct termios old = {0};
    tcgetattr(0, &old);
    old.c_lflag &= ~ICANON;
    old.c_lflag &= ~ECHO;
    old.c_cc[VMIN] = 0;
    old.c_cc[VTIME] = 0;
    tcsetattr(0, TCSANOW, &old);
    read(0, &buf, 1);
    tcsetattr(0, TCSADRAIN, &old);
    return buf;
}

int main() {
    // Configuração do Socket UDP
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    sockaddr_in servaddr;
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(5005);
    servaddr.sin_addr.s_addr = inet_addr("127.0.0.1");

    int throttle = 0, brake = 0, rpm = 1000;
    std::cout << "Simulador C++ Ativo! [W] Acelera, [S] Freia, [L] Lap" << std::endl;

    while (true) {
        char key = getch();
        if (key == 'w') { throttle = std::min(100, throttle + 10); brake = 0; }
        else if (key == 's') { brake = std::min(100, brake + 20); throttle = 0; }
        else if (key == 'l') { std::string lap = "LAP"; sendto(sock, lap.c_str(), lap.length(), 0, (const struct sockaddr *)&servaddr, sizeof(servaddr)); }
        else { // Desaceleração natural
            throttle = std::max(0, throttle - 5);
            brake = std::max(0, brake - 10);
        }

        rpm = 1000 + (throttle * 120);
        
        // Formato: throttle,brake,rpm
        std::string msg = std::to_string(throttle) + "," + std::to_string(brake) + "," + std::to_string(rpm);
        sendto(sock, msg.c_str(), msg.length(), 0, (const struct sockaddr *)&servaddr, sizeof(servaddr));

        usleep(50000); // 20Hz
    }
    return 0;
}