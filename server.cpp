#include "include/json.hpp"
#include <crow.h>
#include <chrono>
#include <thread>
#include <iomanip>
#include <iostream>
#include <atomic>
#include <mutex>
#include <vector>

using json = nlohmann::json;
using namespace std::chrono_literals;

// Funktion zum Senden von Nachrichten an alle verbundenen Clients
void message_sender(std::vector<crow::websocket::connection*>& connections, int value_min, int value_max, std::atomic<bool>& active, std::mutex& conn_mutex) {
    int value = value_min;

    while (active) {
        std::this_thread::sleep_for(10ms); 

        // Wert inkrementieren oder zurücksetzen
        if (value >= value_max) {
            value = value_min;
        } else {
            value++;
        }

        // Zeitstempel mit Millisekunden erstellen
        auto now = std::chrono::system_clock::now();
        auto in_time_t = std::chrono::system_clock::to_time_t(now);
        auto milliseconds = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()) % 1000;

        std::stringstream ss;
        ss << std::put_time(std::localtime(&in_time_t), "%Y-%m-%dT%H:%M:%S");
        ss << '.' << std::setfill('0') << std::setw(3) << milliseconds.count();

        // JSON-Nachricht erstellen
        json message = {
            {"timestamp", ss.str()},
            {"value", value}
        };

        // Nachricht als String konvertieren
        std::string message_str = message.dump();

        // Senden der Nachricht an alle verbundenen Clients
        std::lock_guard<std::mutex> lock(conn_mutex);
        for (auto conn_ptr : connections) {
            try {
                // Nachricht an den Client senden
                conn_ptr->send_text(message_str);

                // Protokollierung der gesendeten Nachricht und der Client-Adresse
                std::cout << "Gesendete Nachricht: " << message_str 
                          << " an Client: " << conn_ptr << std::endl;
            } catch (const std::exception& e) {
                std::cerr << "Fehler beim Senden an Client " << conn_ptr << ": " << e.what() << std::endl;
                // Bei einem Fehler wird das Senden für diesen Client gestoppt
                active = false;
            }
        }
    }

    std::cout << "message_sender Thread beendet." << std::endl;
}

int main() {
    crow::SimpleApp app;

    int value_min = 0;
    int value_max = 255;

    // Liste für aktive Verbindungen und Mutex für Thread-Sicherheit
    std::vector<crow::websocket::connection*> connections;
    std::mutex conn_mutex;

    // Aktivitätsflag zur Steuerung des Threads
    auto active = std::make_shared<std::atomic<bool>>(true);

    // Starten des message_sender Threads
    std::thread([&connections, value_min, value_max, active, &conn_mutex]() mutable {
        message_sender(connections, value_min, value_max, *active, conn_mutex);
    }).detach();

    // WebSocket-Route einrichten
    CROW_WEBSOCKET_ROUTE(app, "/ws")
    .onopen([&connections, &conn_mutex](crow::websocket::connection& conn) {
        std::cout << "WebSocket-Verbindung geöffnet für Client: " << &conn << std::endl;

        // Neue Verbindung zur Liste hinzufügen
        {
            std::lock_guard<std::mutex> lock(conn_mutex);
            connections.push_back(&conn);
        }
    })
    .onclose([&connections, &conn_mutex](crow::websocket::connection& conn, const std::string& reason) {
        std::cout << "WebSocket-Verbindung geschlossen für Client: " << &conn << " Grund: " << reason << std::endl;

        // Verbindung aus der Liste entfernen
        std::lock_guard<std::mutex> lock(conn_mutex);
        connections.erase(std::remove(connections.begin(), connections.end(), &conn), connections.end());
    });

    // Server auf Port 8765 starten
    app.port(8765).multithreaded().run();
    return 0;
}

