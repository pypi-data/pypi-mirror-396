<div class="dash_elem highlight">
    <h2>
        <span class='icon caution'>${api.icon('newspaper')}</span>
        <a href="${request.route_path('activities', _query=dict(__formid__='deform', conseiller_id=request.identity.id))}" title="Voir tous les Rendez-vous & Activités">
            <span>Nouveautés de la dernière version</span>
            ${api.icon('arrow-right')}
        </a>
    </h2>
    <div class='panel-body'>
        % if last_version_resume_es:
            <ul>
                % for resume in last_version_resume_es:
                    <li><span class="icon">${api.icon("star")}</span> ${resume}</li>
                % endfor
                <li><a href="/release_notes?version_es">Voir toutes les nouveautés</a></li>
            </ul>
        % else:
            <p><em>Aucune nouveauté mise en avant</em></p>
        % endif
    </div>
</div>
