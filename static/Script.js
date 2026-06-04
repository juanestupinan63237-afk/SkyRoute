// 1. Envío para Dijkstra
    async function calcularRutaDijkstra() {
        const payload = {
            origin: document.getElementById('routeOrigin').value.toUpperCase().trim(),
            destination: document.getElementById('routeDest').value.toUpperCase().trim(),
            criterion: document.getElementById('routeCriterion').value
        };
        const box = document.getElementById('resultDijkstra');
        box.innerText = "Calculando ruta óptima...";

        try {
            const response = await fetch(`${SERVER_URL}/api/calcular-ruta`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            box.innerText = JSON.stringify(data, null, 2);
        } catch (e) {
            box.innerText = "Error operativo: Verifica que el servidor Flask esté encendido.";
        }
    }

    // 2. Envío para Bloqueos
    async function reportarBloqueo() {
        const payload = {
            originBlocked: document.getElementById('blockOrigin').value.toUpperCase().trim(),
            destinationBlocked: document.getElementById('blockDest').value.toUpperCase().trim(),
            finalDestination: document.getElementById('finalDest').value.toUpperCase().trim(),
            criterion: document.getElementById('blockCriterion').value
        };
        const box = document.getElementById('resultBloqueo');
        box.innerText = "Procesando bloqueo en el grafo y recalculando desvío...";

        try {
            const response = await fetch(`${SERVER_URL}/api/BlockedRoute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            box.innerText = JSON.stringify(data, null, 2);
        } catch (e) {
            box.innerText = "Error operativo: No se pudo contactar al centro de control (Backend).";
        }
    }

    // 3. Envío para DFS
    async function optimizarViaje() {
        const payload = {
            origin: document.getElementById('optOrigin').value.toUpperCase().trim(),
            budget: document.getElementById('optBudget').value,
            limit: document.getElementById('optLimit').value
        };
        const box = document.getElementById('resultOptimizar');
        box.innerText = "Ejecutando simulación DFS con Backtracking combinando las 3 aeronaves...";

        try {
            const response = await fetch(`${SERVER_URL}/api/optimize`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            box.innerText = JSON.stringify(data, null, 2);
        } catch (e) {
            box.innerText = "Error operativo: Falla en la respuesta del motor de optimización.";
        }
    }

    async function getTraveler() {
        let id = document.getElementById ("Id_Traveler_Search").value;
        const response = await fetch ("/traveler/get" , 
            {
                method = "POST",
                headers =  {'Content-Type': 'application/json'},
                body = {"id" : id}
            }
        );
        document.getElementById ("resultTraveler").innerText = await response.json();
    }