from flask import Blueprint, render_template, session, flash, redirect, url_for
from models import models
from routes.utils import login_required

map_bp = Blueprint("map", __name__)


@map_bp.route("/map/<realm_key>")
@login_required
def civilization_map(realm_key):
    user_id = session["user_id"]
    realm = models.get_realm_by_key(realm_key)

    if not realm:
        flash("That realm does not exist.", "error")
        return redirect(url_for("realms.realm_selection"))

    # The map is available for exploration as soon as the realm is active.
    # Students can open it from the dashboard and continue learning even before
    # finishing every level, while the level flow still remains intact.
    sites = models.get_sites_for_realm(realm["id"])
    return render_template("map.html", realm=realm, sites=sites)
