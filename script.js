document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const volunteersRow = document.getElementById('volunteersRow');
    const pagination = document.getElementById('pagination');
    const loading = document.getElementById('loading');
    let currentPage = 1;
    let totalPages = 1;

    // Gestion de la soumission du formulaire
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        currentPage = 1;
        searchVolunteers();
    });

    // Fonction de recherche
    function searchVolunteers() {
        const nom = document.getElementById('nom').value;
        const prenom = document.getElementById('prenom').value;

        loading.style.display = 'block';
        volunteersRow.innerHTML = '';
        pagination.innerHTML = '';

        fetch('/api/volunteers/search?nom=${encodeURIComponent(nom)}&prenom=${encodeURIComponent(prenom)}&page=${currentPage}')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erreur réseau');
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    displayResults(data.data);
                    setupPagination(data.pagination);
                } else {
                    throw new Error(data.message || 'Erreur inconnue');
                }
            })
            .catch(error => {
                volunteersRow.innerHTML = `
                    <div class="col-12">
                        <div class="alert alert-danger">${error.message}</div>
                    </div>
                `;
            })
            .finally(() => {
                loading.style.display = 'none';
            });
    }

    // Affichage des résultats
    function displayResults(volunteers) {
        volunteersRow.innerHTML = '';

        if (volunteers.length === 0) {
            volunteersRow.innerHTML = `
                <tr>
                    <td colspan="7">Aucun bénévole trouvé</td>
                </tr>
            `;
            return;
        }

        volunteers.forEach(volunteer => {
            const tr = document.createElement('tr');
            tr.innerHTML = `

                    <td>${volunteer.nom}</td>
                    <td>${volunteer.prenom}</td>
                    <td>${volunteer.email}</td>
                    <td>${volunteer.telephone}</td>
                    <td>${volunteer.motivation}</td>
                    <td>${volunteer.created_at}</td>
               
                
            `;
            volunteersRow.appendChild(tr);
        });
    }

    // Configuration de la pagination
    function setupPagination(paginationData) {
        totalPages = paginationData.total_pages;
        pagination.innerHTML = '';

        if (totalPages <= 1) return;

        // Bouton Précédent
        const prevItem = document.createElement('li');
        prevItem.className = `page-item ${paginationData.current_page === 1 ? 'disabled': ""}`;
        prevItem.innerHTML = `
            <a class="page-link" href="#" aria-label="Previous" ${paginationData.current_page === 1 ? 'tabindex="-1"' : ''}>
                <span aria-hidden="true">&laquo;</span>
            </a>
        `;
        prevItem.addEventListener('click', (e) => {
            e.preventDefault();
            if (currentPage > 1) {
                currentPage--;
                searchVolunteers();
            }
        });
        pagination.appendChild(prevItem);

        // Numéros de page
        for (let i = 1; i <= totalPages; i++) {
            const pageItem = document.createElement('li');
            pageItem.className = `page-item ${i === currentPage ? 'active' : ''}`;
            pageItem.innerHTML = <a class="page-link" href="#">${i}</a>;
            pageItem.addEventListener('click', (e) => {
                e.preventDefault();
                currentPage = i;
                searchVolunteers();
            });
            pagination.appendChild(pageItem);
        }

        // Bouton Suivant
        const nextItem = document.createElement('li');
        nextItem.className = `page-item ${paginationData.current_page === totalPages ? 'disabled' : ''}`;
        nextItem.innerHTML = `
            <a class="page-link" href="#" aria-label="Next" ${paginationData.current_page === totalPages ? 'tabindex="-1"' : ''}>
                <span aria-hidden="true">&raquo;</span>
            </a>
        `;
        nextItem.addEventListener('click', (e) => {
            e.preventDefault();
            if (currentPage < totalPages) {
                currentPage++;
                searchVolunteers();
            }
        });
        pagination.appendChild(nextItem);
    }

    // Recherche initiale au chargement
    searchVolunteers();
});