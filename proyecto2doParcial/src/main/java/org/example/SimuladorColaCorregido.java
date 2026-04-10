package org.example;
import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;
import java.util.Queue;
import java.util.LinkedList;
import java.util.Random;

public class SimuladorColaCorregido extends JFrame {
    // Modelo de tabla para mostrar resultados
    private DefaultTableModel modeloTabla;
    // Área de texto para mostrar el log de eventos
    private JTextArea areaLog;
    // Botones de simulación y exportación
    private JButton btnSimular, btnExportar;
    // Campos de entrada
    private JTextField txtLlegada, txtServicio;
    private JComboBox<Integer> comboServidores;
    // Progreso
    private JProgressBar progreso;
    // Almacenar estadísticas por corrida
    private List<EstadisticasCorrida> estadisticas = new ArrayList<>();

    public SimuladorColaCorregido() {
        setTitle("Simulador de Fila - Proyecto Estadística");
        setSize(1100, 700);
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setLayout(new BorderLayout());

        // Tabla con columnas para estadísticas por corrida
        modeloTabla = new DefaultTableModel(new String[]{
                "Corrida", "Clientes", "Espera Promedio", "Espera Max", "Tiempo Sistema", "Servidor Ocioso %"
        }, 0);
        JTable tabla = new JTable(modeloTabla);
        JScrollPane scrollTabla = new JScrollPane(tabla);

        areaLog = new JTextArea();
        areaLog.setEditable(false);
        JScrollPane scrollLog = new JScrollPane(areaLog);

        // Panel de configuración
        JPanel panelConfig = new JPanel(new GridLayout(2, 2, 10, 10));
        panelConfig.setBorder(BorderFactory.createTitledBorder("Configuración"));
        panelConfig.add(new JLabel("Tasa de llegada (min):"));
        txtLlegada = new JTextField("3");
        panelConfig.add(txtLlegada);

        panelConfig.add(new JLabel("Tasa de servicio (min):"));
        txtServicio = new JTextField("3");
        panelConfig.add(txtServicio);

        panelConfig.add(new JLabel("Número de servidores:"));
        comboServidores = new JComboBox<>(new Integer[]{1, 2, 3, 4, 5, 6, 7, 8, 9, 10});
        comboServidores.setSelectedItem(2);
        panelConfig.add(comboServidores);

        // Panel de botones y progreso
        JPanel panelBotones = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 10));
        btnSimular = new JButton("Simular 30 corridas");
        btnExportar = new JButton("Exportar CSV");
        progreso = new JProgressBar(0, 30);
        progreso.setStringPainted(true);
        progreso.setVisible(false);
        panelBotones.add(btnSimular);
        panelBotones.add(btnExportar);
        panelBotones.add(progreso);

        // Layout
        JPanel panelCentral = new JPanel(new BorderLayout());
        panelCentral.add(scrollTabla, BorderLayout.CENTER);
        panelCentral.add(scrollLog, BorderLayout.EAST);

        add(panelCentral, BorderLayout.CENTER);
        add(panelConfig, BorderLayout.NORTH);
        add(panelBotones, BorderLayout.SOUTH);

        // Listeners
        btnSimular.addActionListener(e -> iniciarSimulacion());
        btnExportar.addActionListener(e -> exportarCSV());
    }

    // Clase Cliente
    static class Cliente {
        int id, llegada, inicio, salida, espera;
        Cliente(int id, int llegada) {
            this.id = id;
            this.llegada = llegada;
        }
    }

    // Clase para almacenar estadísticas de una corrida
    static class EstadisticasCorrida {
        int numCorrida, numClientes, esperaPromedio, esperaMax, tiempoSistemaPromedio;
        double servidorOciosoPromedio;
        EstadisticasCorrida(int corrida, int clientes, int espProm, int espMax, int tSist, double ocioso) {
            numCorrida = corrida;
            numClientes = clientes;
            esperaPromedio = espProm;
            esperaMax = espMax;
            tiempoSistemaPromedio = tSist;
            servidorOciosoPromedio = ocioso;
        }
    }

    // Ejecuta la simulación en un thread background para no bloquear la UI
    private void iniciarSimulacion() {
        btnSimular.setEnabled(false);
        progreso.setVisible(true);
        progreso.setValue(0);
        modeloTabla.setRowCount(0);
        areaLog.setText("");
        estadisticas.clear();

        int tasaLlegada = Integer.parseInt(txtLlegada.getText());
        int tasaServicio = Integer.parseInt(txtServicio.getText());
        int servidores = (Integer) comboServidores.getSelectedItem();

        SwingWorker<Void, Integer> worker = new SwingWorker<Void, Integer>() {
            @Override
            protected Void doInBackground() throws Exception {
                Random random = new Random();
                for (int corrida = 1; corrida <= 30; corrida++) {
                    Queue<Cliente> cola = new LinkedList<>();
                    int idCliente = 1; // RESETEAR por corrida
                    int tiempoActual = 0;
                    int[] tiempoServidorLibre = new int[servidores];
                    int esperaTotal = 0, esperaMax = 0, tiempoSistemaTotal = 0;

                    // Generar 50 clientes
                    for (int i = 0; i < 50; i++) {
                        tiempoActual += random.nextInt(tasaLlegada) + 1;
                        Cliente c = new Cliente(idCliente++, tiempoActual);
                        cola.add(c);
                    }

                    // Procesar cola FIFO (ahora correctamente)
                    while (!cola.isEmpty()) {
                        Cliente c = cola.poll(); // FIFO: remover primero
                        
                        // Buscar servidor más pronto disponible
                        int servidor = 0;
                        for (int s = 1; s < servidores; s++) {
                            if (tiempoServidorLibre[s] < tiempoServidorLibre[servidor]) {
                                servidor = s;
                            }
                        }

                        c.inicio = Math.max(c.llegada, tiempoServidorLibre[servidor]);
                        c.espera = c.inicio - c.llegada;
                        int duracionServicio = random.nextInt(tasaServicio) + 1;
                        c.salida = c.inicio + duracionServicio;
                        tiempoServidorLibre[servidor] = c.salida;

                        esperaTotal += c.espera;
                        esperaMax = Math.max(esperaMax, c.espera);
                        tiempoSistemaTotal += (c.salida - c.llegada);
                    }

                    // Calcular estadísticas
                    int esperaPromedio = esperaTotal / 50;
                    int tiempoSistemaPromedio = tiempoSistemaTotal / 50;
                    int tiempoSistemaTotal_final = 0;
                    for (int ts : tiempoServidorLibre) {
                        tiempoSistemaTotal_final = Math.max(tiempoSistemaTotal_final, ts);
                    }
                    double ociosoPromedio = 100.0 * (1.0 - (double)tiempoSistemaTotal / (tiempoSistemaTotal_final * servidores));

                    EstadisticasCorrida est = new EstadisticasCorrida(corrida, 50, esperaPromedio, esperaMax, tiempoSistemaPromedio, ociosoPromedio);
                    estadisticas.add(est);

                    publish(corrida);
                    Thread.sleep(50); // Pequeña pausa para no saturar
                }
                return null;
            }

            @Override
            protected void process(List<Integer> chunks) {
                for (Integer corrida : chunks) {
                    EstadisticasCorrida est = estadisticas.get(corrida - 1);
                    modeloTabla.addRow(new Object[]{
                            est.numCorrida,
                            est.numClientes,
                            String.format("%.1f", (double) est.esperaPromedio),
                            est.esperaMax,
                            String.format("%.1f", (double) est.tiempoSistemaPromedio),
                            String.format("%.1f%%", est.servidorOciosoPromedio)
                    });
                    areaLog.append("Corrida " + corrida + " completada - Espera promedio: " + est.esperaPromedio + " min\n");
                    progreso.setValue(corrida);
                }
            }

            @Override
            protected void done() {
                btnSimular.setEnabled(true);
                progreso.setVisible(false);
                areaLog.append("\n✓ Simulación completada\n");
                calcularEstadisticasGenerales();
            }
        };
        worker.execute();
    }

    // Calcular estadísticas globales de todas las corridas
    private void calcularEstadisticasGenerales() {
        if (estadisticas.isEmpty()) return;
        
        double espProm = estadisticas.stream().mapToDouble(e -> e.esperaPromedio).average().orElse(0);
        double espVar = estadisticas.stream().mapToDouble(e -> Math.pow(e.esperaPromedio - espProm, 2)).average().orElse(0);
        double espDesv = Math.sqrt(espVar);
        
        areaLog.append("\n=== Estadísticas Generales (30 corridas) ===\n");
        areaLog.append(String.format("Espera Promedio: %.2f ± %.2f min\n", espProm, espDesv));
        areaLog.append(String.format("Espera Max: %d min\n", estadisticas.stream().mapToInt(e -> e.esperaMax).max().orElse(0)));
    }

    // Exportar a CSV - TODOS los clientes (1500 registros)
    private void exportarCSV() {
        try {
            PrintWriter pw = new PrintWriter(new FileWriter("resultados_estadisticas.csv"));
            // Encabezado con columnas obligatorias
            pw.println("ID_Cliente,Tiempo_Llegada,Tiempo_Inicio_Servicio,Tiempo_Salida,Tiempo_Espera_Fila");
            
            // Recorrer todas las corridas y generar los datos nuevamente
            int tasaLlegada = Integer.parseInt(txtLlegada.getText());
            int tasaServicio = Integer.parseInt(txtServicio.getText());
            int servidores = (Integer) comboServidores.getSelectedItem();
            
            Random random = new Random(42); // Seed fijo para reproducibilidad
            int idClienteGlobal = 1;
            
            for (int corrida = 1; corrida <= 30; corrida++) {
                Queue<Cliente> cola = new LinkedList<>();
                int idCliente = 1;
                int tiempoActual = 0;
                int[] tiempoServidorLibre = new int[servidores];
                
                // Generar 50 clientes para esta corrida
                for (int i = 0; i < 50; i++) {
                    tiempoActual += random.nextInt(tasaLlegada) + 1;
                    Cliente c = new Cliente(idClienteGlobal++, tiempoActual);
                    cola.add(c);
                }
                
                // Procesar la cola
                while (!cola.isEmpty()) {
                    Cliente c = cola.poll();
                    
                    // Buscar servidor más pronto disponible
                    int servidor = 0;
                    for (int s = 1; s < servidores; s++) {
                        if (tiempoServidorLibre[s] < tiempoServidorLibre[servidor]) {
                            servidor = s;
                        }
                    }
                    
                    c.inicio = Math.max(c.llegada, tiempoServidorLibre[servidor]);
                    c.espera = c.inicio - c.llegada;
                    int duracionServicio = random.nextInt(tasaServicio) + 1;
                    c.salida = c.inicio + duracionServicio;
                    tiempoServidorLibre[servidor] = c.salida;
                    
                    // Escribir cada cliente en el CSV
                    pw.println(String.format("%d,%d,%d,%d,%d",
                            c.id, c.llegada, c.inicio, c.salida, c.espera));
                }
            }
            
            pw.close();
            JOptionPane.showMessageDialog(this, "✓ Datos exportados a resultados_estadisticas.csv\n" +
                    "Total: 1500 registros (30 corridas × 50 clientes)");
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(this, "Error: " + ex.getMessage());
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new SimuladorColaCorregido().setVisible(true));
    }
}