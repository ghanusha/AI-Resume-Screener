def match_skills(resume_skills, job_skills):
    """
    Matches extracted resume skills against required job skills.
    Calculates percentage score, matched skills, missing skills, and status.
    resume_skills: list of strings
    job_skills: list of strings (required skills)
    """
    if not job_skills:
        return {
            "matched": [],
            "missing": [],
            "score": 0.0,
            "status": "Low"
        }
        
    resume_set = set([s.lower() for s in resume_skills])
    job_set = set([s.lower() for s in job_skills])
    
    matched = list(resume_set.intersection(job_set))
    missing = list(job_set.difference(resume_set))
    
    total_required = len(job_set)
    score = (len(matched) / total_required) * 100 if total_required > 0 else 0
    
    if score >= 75:
        status = "Excellent"
    elif score >= 50:
        status = "Good"
    else:
        status = "Low"
        
    return {
        "matched": matched,
        "missing": missing,
        "score": round(score, 2),
        "status": status
    }
