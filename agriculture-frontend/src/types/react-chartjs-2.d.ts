declare module "react-chartjs-2" {
  import type { ForwardRefExoticComponent, RefAttributes } from "react";
  import type { Chart as ChartJS, ChartData, ChartOptions, ChartTypeRegistry } from "chart.js";

  type Props<TType extends keyof ChartTypeRegistry = "line"> = {
    data: ChartData<TType>;
    options?: ChartOptions<TType>;
  } & RefAttributes<ChartJS<TType>>;

  export const Line: ForwardRefExoticComponent<Props<"line">>;
}
