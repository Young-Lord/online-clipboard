import Swal from "sweetalert2"
import { SweetAlertResult, SweetAlertOptions } from "sweetalert2"
import { $t } from "@/plugins/i18n"

const baseOptions = {
    showClass: { popup: "animate__animated animate__fadeIn animate__faster" },
    confirmButtonText: $t("clip.ok"),
    cancelButtonText: $t("clip.cancel"),
}

export const dangerousOptions = {
    confirmButtonColor: "#d33",
    cancelButtonColor: "#3085d6",
}

export function showDetailWarning(
    options: SweetAlertOptions
): Promise<SweetAlertResult> {
    return Swal.fire({
        ...baseOptions,
        icon: "error",
        ...options,
    })
}

export function showAutoCloseSuccess(
    options: SweetAlertOptions
): Promise<SweetAlertResult> {
    return Swal.fire({
        ...baseOptions,
        icon: "success",
        timer: 1200,
        ...options,
    })
}

export function cancelableInput(
    options: SweetAlertOptions
): Promise<SweetAlertResult> {
    return Swal.fire({
        ...baseOptions,
        showCancelButton: true,
        ...options,
    })
}

export function dangerousConfirm(
    options: SweetAlertOptions
): Promise<SweetAlertResult> {
    return Swal.fire({
        ...baseOptions,
        ...dangerousOptions,
        showCancelButton: true,
        icon: "warning",
        ...options,
    })
}
