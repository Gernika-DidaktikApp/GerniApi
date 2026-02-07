"""
Teacher Dashboard API endpoints
Provides data for teacher dashboard page (class-level statistics)
"""

import io
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user_from_token
from app.services.teacher_dashboard_service import TeacherDashboardService

router = APIRouter(
    prefix="/api/teacher/dashboard",
    tags=["👨‍🏫 Teacher Dashboard"],
    responses={
        422: {"description": "Error de validación"},
    },
)


@router.get(
    "/classes",
    response_model=list[dict[str, str]],
    summary="Get profesor's classes",
    description="Returns all classes for the authenticated profesor",
)
def get_profesor_classes(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_from_token),
) -> list[dict[str, str]]:
    """
    ## Get Profesor's Classes

    Returns all classes assigned to the authenticated profesor.

    ### Returns
    - **id**: Class ID
    - **nombre**: Class name

    ### Authentication
    Requires valid JWT token from profesor login.
    """
    profesor_id = current_user.get("profesor_id")
    if not profesor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only profesores can access this endpoint"
        )

    return TeacherDashboardService.get_profesor_classes(db, profesor_id)


@router.get(
    "/summary",
    response_model=dict[str, Any],
    summary="Get class summary statistics",
    description="Returns summary metrics for a class: students, progress, time, grade",
)
def get_class_summary(
    clase_id: str = Query(None, description="Optional class ID (if None, aggregates all classes)"),
    days: int = Query(7, ge=1, le=365, description="Number of days to look back"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_from_token),
) -> dict[str, Any]:
    """
    ## Get Class Summary

    Returns summary statistics for the teacher's class:
    - **total_alumnos**: Total number of students
    - **progreso_medio**: Average progress percentage (0-100)
    - **tiempo_promedio**: Average time spent in minutes
    - **nota_media**: Average grade (0-10)
    - **clase_nombre**: Name of the class

    ### Parameters
    - **clase_id**: Optional specific class ID (default: all classes)
    - **days**: Number of days to look back (default: 7)

    ### Authentication
    Requires valid JWT token from profesor login.
    """
    profesor_id = current_user.get("profesor_id")
    if not profesor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only profesores can access this endpoint"
        )

    return TeacherDashboardService.get_class_summary(db, profesor_id, clase_id, days)


@router.get(
    "/student-progress",
    response_model=dict[str, list],
    summary="Get progress by student",
    description="Returns progress percentage for each student",
)
def get_student_progress(
    clase_id: str = Query(None, description="Optional class ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_from_token),
) -> dict[str, list]:
    """
    ## Get Student Progress

    Returns progress data for the "Progreso por Alumno" chart:
    - **students**: Array of student names
    - **progress**: Progress percentage (0-100) for each student

    ### Parameters
    - **clase_id**: Optional specific class ID (default: all classes)

    ### Authentication
    Requires valid JWT token from profesor login.
    """
    profesor_id = current_user.get("profesor_id")
    if not profesor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only profesores can access this endpoint"
        )

    return TeacherDashboardService.get_student_progress(db, profesor_id, clase_id)


@router.get(
    "/student-time",
    response_model=dict[str, list],
    summary="Get time spent by student",
    description="Returns time spent for each student",
)
def get_student_time(
    clase_id: str = Query(None, description="Optional class ID"),
    days: int = Query(7, ge=1, le=365, description="Number of days to look back"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_from_token),
) -> dict[str, list]:
    """
    ## Get Student Time

    Returns time data for the "Tiempo Dedicado por Alumno" chart:
    - **students**: Array of student first names
    - **time**: Time spent in minutes for each student

    ### Parameters
    - **clase_id**: Optional specific class ID (default: all classes)
    - **days**: Number of days to look back (default: 7)

    ### Authentication
    Requires valid JWT token from profesor login.
    """
    profesor_id = current_user.get("profesor_id")
    if not profesor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only profesores can access this endpoint"
        )

    return TeacherDashboardService.get_student_time(db, profesor_id, clase_id, days)


@router.get(
    "/activities-by-class",
    response_model=dict[str, Any],
    summary="Get activities completion by class",
    description="Returns activity completion status (completed, in progress, not started)",
)
def get_activities_by_class(
    clase_id: str = Query(None, description="Optional class ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_from_token),
) -> dict[str, Any]:
    """
    ## Get Activities by Class

    Returns activity completion data for the "Actividades Completadas" chart:
    - **activities**: Array of activity names
    - **completed**: Number of students who completed each activity
    - **in_progress**: Number of students with activity in progress
    - **not_started**: Number of students who haven't started

    ### Parameters
    - **clase_id**: Optional specific class ID (default: all classes)

    ### Authentication
    Requires valid JWT token from profesor login.
    """
    profesor_id = current_user.get("profesor_id")
    if not profesor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only profesores can access this endpoint"
        )

    return TeacherDashboardService.get_activities_by_class(db, profesor_id, clase_id)


@router.get(
    "/class-evolution",
    response_model=dict[str, Any],
    summary="Get class evolution over time",
    description="Returns progress and grade evolution over time",
)
def get_class_evolution(
    clase_id: str = Query(None, description="Optional class ID"),
    days: int = Query(14, ge=1, le=365, description="Number of days to retrieve"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_from_token),
) -> dict[str, Any]:
    """
    ## Get Class Evolution

    Returns evolution data for the "Evolución de la Clase" chart:
    - **dates**: Array of date strings (YYYY-MM-DD)
    - **progress**: Average progress percentage for each date
    - **grades**: Average grade for each date

    ### Parameters
    - **clase_id**: Optional specific class ID (default: all classes)
    - **days**: Number of days to retrieve (default: 14)

    ### Authentication
    Requires valid JWT token from profesor login.
    """
    profesor_id = current_user.get("profesor_id")
    if not profesor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only profesores can access this endpoint"
        )

    return TeacherDashboardService.get_class_evolution(db, profesor_id, clase_id, days)


@router.get(
    "/students-list",
    response_model=list[dict[str, Any]],
    summary="Get detailed students list",
    description="Returns detailed list of students with progress, time, and grades",
)
def get_students_list(
    clase_id: str = Query(None, description="Optional class ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_from_token),
) -> list[dict[str, Any]]:
    """
    ## Get Students List

    Returns detailed information for each student:
    - **nombre**: Student full name
    - **username**: Student username
    - **progreso**: Progress percentage (0-100)
    - **tiempo_total**: Total time spent in minutes
    - **nota_media**: Average grade (0-10)
    - **actividades_completadas**: Number of completed activities
    - **ultima_actividad**: Date of last activity

    ### Parameters
    - **clase_id**: Optional specific class ID (default: all classes)

    ### Authentication
    Requires valid JWT token from profesor login.
    """
    profesor_id = current_user.get("profesor_id")
    if not profesor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only profesores can access this endpoint"
        )

    return TeacherDashboardService.get_students_list(db, profesor_id, clase_id)


@router.get(
    "/export-students-csv",
    summary="Export students list to CSV",
    description="Downloads students list as CSV file",
)
def export_students_csv(
    clase_id: str = Query(None, description="Optional class ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_from_token),
):
    """
    ## Export Students List to CSV

    Downloads a CSV file with detailed student information.

    ### Parameters
    - **clase_id**: Optional specific class ID (default: all classes)

    ### Authentication
    Requires valid JWT token from profesor login.
    """
    profesor_id = current_user.get("profesor_id")
    if not profesor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only profesores can access this endpoint"
        )

    csv_content = TeacherDashboardService.export_students_csv(db, profesor_id, clase_id)

    # Create filename with current date
    from datetime import datetime

    filename = f"alumnos_{datetime.now().strftime('%Y%m%d')}.csv"

    return StreamingResponse(
        io.BytesIO(csv_content.encode("utf-8-sig")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get(
    "/export-students-excel",
    summary="Export students list to Excel",
    description="Downloads students list as Excel file",
)
def export_students_excel(
    clase_id: str = Query(None, description="Optional class ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_from_token),
):
    """
    ## Export Students List to Excel

    Downloads an Excel file with detailed student information.

    ### Parameters
    - **clase_id**: Optional specific class ID (default: all classes)

    ### Authentication
    Requires valid JWT token from profesor login.
    """
    profesor_id = current_user.get("profesor_id")
    if not profesor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only profesores can access this endpoint"
        )

    excel_bytes = TeacherDashboardService.export_students_excel(db, profesor_id, clase_id)

    # Create filename with current date
    from datetime import datetime

    filename = f"alumnos_{datetime.now().strftime('%Y%m%d')}.xlsx"

    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.post(
    "/cache/clear",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear teacher dashboard cache",
    description="Clears all cached teacher dashboard data",
)
def clear_teacher_dashboard_cache(
    current_user: dict = Depends(get_current_user_from_token),
):
    """
    ## Clear Teacher Dashboard Cache

    Clears all cached teacher dashboard data to force fresh queries on next request.

    Returns HTTP 204 (No Content) on success.

    ### Authentication
    Requires valid JWT token from profesor login.
    """
    profesor_id = current_user.get("profesor_id")
    if not profesor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only profesores can access this endpoint"
        )

    TeacherDashboardService.clear_cache()
    return None
